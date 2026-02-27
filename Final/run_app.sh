#!/usr/bin/env zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
	echo "Project virtual environment not found at $PYTHON_BIN"
	echo "Create it first: python3 -m venv $PROJECT_ROOT/.venv"
	exit 1
fi

exec "$PYTHON_BIN" -m streamlit run "$SCRIPT_DIR/streamlit_app.py" "$@"