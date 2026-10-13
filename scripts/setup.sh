#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mvn -B -DskipTests compile
python3 -m pip install -r python-tests/requirements.txt
echo "Setup complete. Run scripts/run-tests.sh"
