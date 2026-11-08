#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
VERSEFLOW_PYTHON="${VERSEFLOW_PYTHON:-.venv/bin/python}"
if [[ ! -x "$VERSEFLOW_PYTHON" ]]; then
    echo 'Create the environment first: ./setup.sh' >&2
    exit 1
fi
"$VERSEFLOW_PYTHON" -m pip install 'pyinstaller>=6,<7'
"$VERSEFLOW_PYTHON" -m PyInstaller --noconfirm --clean --name VerseFlow --add-data 'assets/logo.png:assets' verseflow.py
version="$("$VERSEFLOW_PYTHON" verseflow.py --version)"
version="${version#VerseFlow }"
arch="$(uname -m)"
bundle="dist/VerseFlow-linux-${arch}-${version}"
mkdir -p "$bundle/assets" "$bundle/packaging"
cp -a dist/VerseFlow "$bundle/"
cp assets/logo.png "$bundle/assets/"
cp packaging/verseflow.desktop "$bundle/packaging/"
cp install.sh README.md CREDITS.md LICENSE "$bundle/"
tar -C dist -czf "${bundle}.tar.gz" "${bundle#dist/}"
echo "Built: ${bundle}.tar.gz"
