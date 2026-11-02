# Jeevan Saathi AI (Streamlit)
Run locally: `pip install -r requirements.txt` then `streamlit run app.py`

Deploy: push this folder to GitHub, open share.streamlit.io, choose the repo, main file `app.py`.

Optional real AI chat: in the app's Settings > Secrets add `ANTHROPIC_API_KEY = "your-key"`.
Without it the assistant gives sample answers.
Note: accounts/tasks are stored in `jsa.db`, which Streamlit Cloud may reset on restart.
