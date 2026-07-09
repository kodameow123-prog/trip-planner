#!/bin/bash
# Quick launch — runs Flask backend + serves frontend on localhost:5000
set -e

if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "⚠️  OPENROUTER_API_KEY not set. Run: export OPENROUTER_API_KEY=sk-or-..."
  exit 1
fi

cd "$(dirname "$0")/api"

# Install deps if missing
python3 -c "import flask" 2>/dev/null || pip3 install flask

echo "🚀 Launching Trip Planner on http://localhost:5000"
python3 index.py
