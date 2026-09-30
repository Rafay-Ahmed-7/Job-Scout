import json
from pathlib import Path
import streamlit as st

PROFILE_FILE = Path("profile.json")

def load_profile():
    return json.loads(PROFILE_FILE.read_text()) if PROFILE_FILE.exists() else {}

def save_profile(p):
    PROFILE_FILE.write_text(json.dumps(p, indent=2))

def score_job(profile, title, description, location=""):
    text = f"{title} {description}".lower()
    title_l = title.lower()
    score = 0
    reasons, warnings = [], []

    role_hits = [r for r in profile["roles"] if r.lower() in title_l]
    if role_hits:
        score += 30
        reasons.append("Target role matches your career direction")

    skill_hits = [s for s in profile["skills"] if s.lower() in text]
    score += min(45, len(skill_hits) * 4)
    if skill_hits:
        reasons.append(f"{len(skill_hits)} relevant skills found")

    if "karachi" in location.lower():
        score += 15
        reasons.append("Karachi location match")

    for term in profile["exclude_terms"]:
        if term in text:
            score -= 35
            warnings.append(f"Contains excluded term: {term}")
            break

    if any(x in title_l for x in ["intern", "trainee"]):
        score -= 40
        warnings.append("Internship/trainee role")

    score = max(0, min(100, score))
    verdict = "STRONG APPLY 🔥" if score >= 85 else "GOOD MATCH ⭐" if score >= 70 else "REVIEW ⚠️" if score >= 55 else "SKIP"
    return score, verdict, reasons, warnings, skill_hits

def search_urls(profile):
    q = " OR ".join(f'"{r}"' for r in profile["roles"][:6])
    enc = q.replace(" ", "%20").replace('"', "%22")
    return (
        f"https://www.linkedin.com/jobs/search/?keywords={enc}&location=Karachi",
        f"https://pk.indeed.com/jobs?q={enc}&l=Karachi"
    )

st.set_page_config(page_title="Rafay Job Scout", page_icon="🎯", layout="wide")
profile = load_profile()

st.title("🎯 Rafay Job Scout")
st.caption("Fast personal job-matching MVP — discovery + scoring, not auto-apply.")

with st.sidebar:
    st.header("⚙️ Profile & filters")
    profile["min_salary"] = st.number_input("Minimum salary (PKR)", min_value=0, value=int(profile["min_salary"]), step=5000)
    profile["preferred_salary"] = st.number_input("Preferred salary (PKR)", min_value=0, value=int(profile["preferred_salary"]), step=5000)
    profile["experience_years"] = st.number_input("Experience (years)", min_value=0, value=int(profile["experience_years"]), step=1)

    roles = st.text_area("Target roles", "\n".join(profile["roles"]))
    skills = st.text_area("Skills", "\n".join(profile["skills"]))
    excluded = st.text_area("Never show", "\n".join(profile["exclude_terms"]))

    if st.button("💾 Save profile", use_container_width=True):
        profile["roles"] = [x.strip() for x in roles.splitlines() if x.strip()]
        profile["skills"] = [x.strip() for x in skills.splitlines() if x.strip()]
        profile["exclude_terms"] = [x.strip().lower() for x in excluded.splitlines() if x.strip()]
        save_profile(profile)
        st.success("Saved.")

linkedin, indeed = search_urls(profile)
st.subheader("1. Find jobs")
a, b = st.columns(2)
with a:
    st.link_button("Open LinkedIn search ↗", linkedin, use_container_width=True)
with b:
    st.link_button("Open Indeed search ↗", indeed, use_container_width=True)

st.info("V1 intentionally avoids login, private scraping and auto-apply. Open the source, copy a promising public listing, and let the bot rank it.")

st.subheader("2. Score a job")
title = st.text_input("Job title")
location = st.text_input("Location", "Karachi")
salary = st.text_input("Salary shown (optional)", placeholder="e.g. PKR 80,000 - 120,000")
description = st.text_area("Paste job description", height=250)

if st.button("🎯 Score this job", type="primary"):
    if not title or not description:
        st.warning("Enter a job title and description.")
    else:
        score, verdict, reasons, warnings, hits = score_job(profile, title, description, location)
        st.metric("Match score", f"{score}/100")
        st.success(verdict)
        if reasons:
            st.markdown("**Why it matches:**")
            for x in reasons: st.write("✓ " + x)
        if hits:
            st.markdown("**Matched skills:** " + ", ".join(hits))
        if warnings:
            st.markdown("**Warnings:**")
            for x in warnings: st.write("⚠ " + x)

st.subheader("3. Planned next")
st.write("Public/permitted job discovery → duplicate detection → salary parsing → saved jobs → Telegram daily alerts.")
