# Zomato AI — Restaurant Recommendation System

[![GitHub](https://img.shields.io/badge/GitHub-arthims%2Fzomato--ai-blue?logo=github)](https://github.com/arthims/zomato-ai)

AI-powered restaurant recommendations using the HuggingFace Zomato dataset and Groq LLM (llama-3.3-70b-versatile).

---

## Quick start

```bash
git clone https://github.com/arthims/zomato-ai
cd zomato-ai

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"

cp .env.example .env             # add GROQ_API_KEY
milestone1 doctor                # verify environment
```

## Run locally

```bash
bash run.sh
# Backend  → http://localhost:8000
# Frontend → http://localhost:3000
# API docs → http://localhost:8000/docs
```

Or separately:

```bash
# backend
uvicorn milestone1.phase6_api.app:app --reload --port 8000

# frontend
cd frontend && npm install && npm run dev
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Get from https://console.groq.com/keys |
| `GROQ_MODEL` | optional | Default: `llama-3.3-70b-versatile` |
| `HF_TOKEN` | optional | Raises HuggingFace rate limits |
| `CORS_ORIGINS` | production | Comma-separated allowed origins |
| `CANDIDATE_CAP` | optional | Max candidates sent to LLM (default 20) |

## Project structure

```
zomato-ai/
├── src/milestone1/
│   ├── phase0/             # Scope · paths · settings · CLI
│   ├── phase1_ingestion/   # HuggingFace dataset · normalize · deduplicate
│   ├── phase2_preferences/ # UserPreferences · validation · fuzzy city match
│   ├── phase3_integration/ # Filter · rank · prompt builder
│   ├── phase4_llm/         # Groq client · rankings parser · fallback
│   ├── phase5_output/      # Renderer · empty states · telemetry
│   └── phase6_api/         # FastAPI · /health · /meta · /recommendations
├── frontend/               # Next.js 15 · TypeScript · Tailwind CSS
│   ├── app/                # page.tsx · layout.tsx
│   ├── components/         # PreferenceForm · ResultCard · EmptyState · ...
│   ├── lib/api.ts          # Typed fetch wrapper
│   └── types/index.ts      # Shared TypeScript types
├── docs/
│   ├── phased-architecture.md
│   ├── edge-cases.md
│   ├── dataset-contract.md
│   └── stitch-ui-prompt.md
├── tests/                  # Per-phase dedicated test files + fixtures
├── run.sh                  # Start backend + frontend together
├── .env.example
└── pyproject.toml
```

## CLI commands

| Command | Phase | Description |
|---|---|---|
| `milestone1 info` | 0 | Project info and stack |
| `milestone1 doctor` | 0 | Environment health checks |
| `milestone1 ingest-smoke` | 1 | Load and print sample rows |
| `milestone1 prefs-parse` | 2 | Parse and validate preferences |
| `milestone1 prompt-build` | 3 | Build prompt payload (no LLM call) |
| `milestone1 recommend` | 4 | Get LLM-ranked recommendations |
| `milestone1 recommend-run` | 5 | End-to-end run with formatted output |

## Deployment

| Option | Services | Command |
|---|---|---|
| Production | Render (backend) + Vercel (frontend) | See `docs/phased-architecture.md` Phase 8 |
| Demo | Streamlit Community Cloud | `streamlit run streamlit_app.py` |

## Tests

```bash
python tests/test_phase1_dedicated.py
python tests/test_phase2_dedicated.py
python tests/test_phase3_dedicated.py
python tests/test_phase4_dedicated.py
python tests/test_phase4_live_example.py   # Bellandur · ₹2000 · 4.0★
```
