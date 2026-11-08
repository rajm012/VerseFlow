#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x .venv/bin/python ]]; then
    ./setup.sh
fi
exec .venv/bin/python verseflow.py --panel "$@"
