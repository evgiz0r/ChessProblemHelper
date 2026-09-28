#!/bin/bash
# Install python-chess for Claude Code on the web sessions.
# --use-pep517: the legacy setup.py build of chess>=1.11 fails with the system pip/setuptools.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
python3 -c "import chess, sys; sys.exit(0 if tuple(map(int, chess.__version__.split('.')[:2])) >= (1, 11) else 1)" 2>/dev/null \
  || pip install -q --use-pep517 -r requirements.txt
