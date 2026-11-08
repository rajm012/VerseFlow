#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
source_app=dist/VerseFlow
if [[ -x VerseFlow/VerseFlow ]]; then
    source_app=VerseFlow
fi
if [[ ! -x "$source_app/VerseFlow" ]]; then
    echo 'Build the app first with ./build.sh, or extract a Linux release archive.' >&2
    exit 1
fi
data_dir="${XDG_DATA_HOME:-$HOME/.local/share}"
app_dir="$data_dir/verseflow"
bin_dir="${VERSEFLOW_BIN_DIR:-$HOME/.local/bin}"
mkdir -p "$app_dir" "$bin_dir" "$data_dir/applications" "$data_dir/icons/hicolor/256x256/apps"
cp -a "$source_app/." "$app_dir/"
cp assets/logo.png "$data_dir/icons/hicolor/256x256/apps/verseflow.png"
python3 - "$app_dir/VerseFlow" "$bin_dir/verseflow" <<'PY'
import pathlib, shlex, sys
launcher = pathlib.Path(sys.argv[2])
launcher.write_text('#!/bin/sh\nexec ' + shlex.quote(sys.argv[1]) + ' --panel "$@"\n')
launcher.chmod(0o755)
PY
python3 - "$bin_dir/verseflow" packaging/verseflow.desktop "$data_dir/applications/verseflow.desktop" <<'PY'
import pathlib, sys
executable = sys.argv[1]
executable = executable.replace('%', '%%')
for old, new in (('\\', '\\\\'), ('"', '\\"'), ('`', '\\`'), ('$', '\\$')):
    executable = executable.replace(old, new)
text = pathlib.Path(sys.argv[2]).read_text().replace('Exec=verseflow', 'Exec="' + executable + '"')
pathlib.Path(sys.argv[3]).write_text(text)
PY
echo 'Installed for your user. Open VerseFlow from the applications menu.'
