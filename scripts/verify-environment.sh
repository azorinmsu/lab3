#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
check() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing: $1"
    fail=1
  else
    echo "found: $1 ($($1 --version 2>&1 | head -n 1))"
  fi
}

check java
check mvn
check python3

if python3 -c "import jpype, pytest" >/dev/null 2>&1; then
  echo "found: jpype and pytest"
else
  echo "missing: Python packages from python-tests/requirements.txt"
  echo "  python3 -m pip install -r python-tests/requirements.txt"
  fail=1
fi

if [[ ! -d target/classes ]]; then
  echo "missing: target/classes (run mvn -B -DskipTests compile)"
  fail=1
else
  echo "found: target/classes"
fi

exit "$fail"
