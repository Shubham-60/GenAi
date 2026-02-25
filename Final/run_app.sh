#!/usr/bin/env zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"

exec python -m streamlit run "$SCRIPT_DIR/streamlit_app.py" "$@"