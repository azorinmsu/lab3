#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mvn -B test
python3 -m pytest python-tests -q
