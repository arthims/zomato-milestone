#!/usr/bin/env bash
# run.sh — start backend (FastAPI) and frontend (Next.js) together
# Usage: bash run.sh
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND="$ROOT/frontend"
ENV="$ROOT/.env"

# ── load .env ──────────────────────────────────────────────────────────────
if [ -f "$ENV" ]; then
  export $(grep -v '^#' "$ENV" | xargs)
  echo "✓ Loaded $ENV"
else
  echo "⚠ No .env found — copy .env.example to .env and add GROQ_API_KEY"
fi

# ── backend ────────────────────────────────────────────────────────────────
echo ""
echo "▶ Starting backend  → http://localhost:8000"
echo "  Docs              → http://localhost:8000/docs"

cd "$ROOT"
uvicorn milestone1.phase6_api.app:app \
  --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# ── frontend ───────────────────────────────────────────────────────────────
echo ""
echo "▶ Starting frontend → http://localhost:3000"

cd "$FRONTEND"

if [ ! -d node_modules ]; then
  echo "  Installing dependencies…"
  npm install --silent
fi

NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev &
FRONTEND_PID=$!

# ── cleanup on exit ────────────────────────────────────────────────────────
trap "echo ''; echo 'Stopping…'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Backend  → http://localhost:8000"
echo "  Frontend → http://localhost:3000"
echo "  Press Ctrl+C to stop both"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

wait
