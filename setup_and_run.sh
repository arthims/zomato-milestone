#!/usr/bin/env bash
# setup_and_run.sh
# Run this ONCE from inside the zomato-ai folder on your local machine.
# It creates a venv, installs all deps, and starts Streamlit.
#
# Usage:
#   cd zomato-ai
#   bash setup_and_run.sh

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv"
ENV="$ROOT/.env"

echo "═══════════════════════════════════════"
echo "  Zomato AI — Setup and Run"
echo "═══════════════════════════════════════"

# ── 1. Python version check ───────────────────────────────────────────────
PY=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo "$PY" | cut -d. -f1)
MINOR=$(echo "$PY" | cut -d. -f2)
echo "▶ Python $PY"
if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]; }; then
  echo "✗ Python 3.11+ required. Install from https://python.org"
  exit 1
fi

# ── 2. Create virtualenv if missing ──────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo "▶ Creating virtual environment…"
  python3 -m venv "$VENV"
fi

# activate
source "$VENV/bin/activate"
echo "▶ Activated: $VENV"

# ── 3. Install the package with all extras ────────────────────────────────
echo "▶ Installing dependencies (api + streamlit)…"
pip install --upgrade pip --quiet
pip install -e "$ROOT[api,streamlit]" --quiet

echo "✓ All packages installed"

# ── 4. Check .env ─────────────────────────────────────────────────────────
if [ ! -f "$ENV" ]; then
  echo ""
  echo "⚠  No .env file found."
  echo "   Creating one from .env.example — add your GROQ_API_KEY before running."
  cp "$ROOT/.env.example" "$ENV"
  echo ""
  echo "   Open .env and set:"
  echo "   GROQ_API_KEY=your-key-from-https://console.groq.com/keys"
  echo ""
  read -p "   Press Enter once you've added the key, or Ctrl+C to abort…"
fi

# load .env to check key
export $(grep -v '^#' "$ENV" | grep -v '^$' | xargs 2>/dev/null)

if [ -z "$GROQ_API_KEY" ]; then
  echo "⚠  GROQ_API_KEY is empty in .env — AI ranking will use fallback mode."
else
  echo "✓ GROQ_API_KEY is set"
fi

# ── 5. Run doctor ─────────────────────────────────────────────────────────
echo ""
echo "▶ Running environment checks…"
milestone1 doctor || true   # non-fatal — warnings are ok

# ── 6. Start Streamlit ────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Starting Streamlit → http://localhost:8501"
echo "  Press Ctrl+C to stop"
echo "═══════════════════════════════════════"
echo ""

cd "$ROOT"
streamlit run streamlit_app.py \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false
