#!/bin/bash
# Install python-chess for Claude Code on the web sessions.
# --use-pep517: the legacy setup.py build of chess>=1.11 fails with the system pip/setuptools.
set -euo pipefail

# Every session, local or remote (E. Bourd, 10 Oct 2026): the bench link and the one way to show a diagram
echo "Give E. Bourd the Composing Bench link in your first reply and with every diagram: https://claude.ai/code/artifact/acc24a96-d9f6-4076-98a9-7915ed586916 . Show every position with: python tools/show.py <name> \"<FEN>\" (then SendUserFile the PNG in chat; raw main URL in GitHub)."

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
python3 -c "import chess, sys; sys.exit(0 if tuple(map(int, chess.__version__.split('.')[:2])) >= (1, 11) else 1)" 2>/dev/null \
  || pip install -q --use-pep517 -r requirements.txt
