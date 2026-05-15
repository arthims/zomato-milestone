# Streamlit Deployment Guide

Single-process demo path — no Node build, no CORS, no two-service setup.

## Run locally

```bash
pip install -e ".[streamlit]"
streamlit run streamlit_app.py
# → http://localhost:8501
```

## Deploy to Streamlit Community Cloud (free)

1. Push repo to GitHub — `https://github.com/arthims/zomato-ai`
2. Go to **share.streamlit.io** → New app → connect the repo
3. Set **Main file path**: `streamlit_app.py`
4. Add secrets under **Settings → Secrets**:

```toml
GROQ_API_KEY = "your-key-here"
GROQ_MODEL   = "llama-3.3-70b-versatile"
```

5. Click **Deploy** — app is live at `https://your-app.streamlit.app`

## Secrets pattern

```python
# Reads st.secrets on Cloud, falls back to .env locally
api_key = st.secrets.get("GROQ_API_KEY") or load_settings().groq_api_key
```

Never commit `GROQ_API_KEY` to the repo.

## Free tier limits

| Limit | Value |
|---|---|
| RAM | 1 GB |
| Sleep | ~5 min idle (wakes in ~30 s) |
| `candidate_cap` | Keep ≤ 20 |

## Smoke test

Open the deployed URL → select **Bellandur** → set budget to **High** →
rating to **4.0** → click **Find Restaurants** → verify 5 ranked cards appear.
