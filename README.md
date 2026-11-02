# Jeevan Saathi AI (Streamlit)
Files: app.py (whole site), i18n.json (original Hindi/Marathi translations), requirements.txt, .streamlit/config.toml.

Run locally: `pip install -r requirements.txt` then `streamlit run app.py`

Deploy: push this folder to GitHub, open share.streamlit.io, choose the repo, main file `app.py`.

Optional real AI chat: in the app's Settings > Secrets add `ANTHROPIC_API_KEY = "your-key"`.
Without it the assistant gives the original sample answers.

Accounts/tasks are stored in `jsa.db` (SQLite). Streamlit Cloud may reset it on restart.
