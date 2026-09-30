# Rafay Job Scout V1

## Run on Windows

```powershell
cd job_scout_v1
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

This V1 is intentionally small. It stores your profile locally, generates targeted LinkedIn/Indeed searches, and scores pasted job listings. It does not log in, scrape private content, or auto-apply.
