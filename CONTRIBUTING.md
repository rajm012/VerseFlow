# Contributing to VerseFlow

This is a Linux desktop project maintained by
[rajm012](https://github.com/rajm012). Contributions should work with the
existing MPRIS/D-Bus integration, Qt interface, and Linux packaging.

## Development setup

Use Python 3.10 or newer and a graphical Linux session. On Ubuntu/Debian:

```bash
sudo apt install python3-venv dbus xvfb xauth libxcb-cursor0 libxkbcommon-x11-0
./setup.sh
.venv/bin/python -m pip install -r requirements-dev.txt
./run.sh --no-tray
```

Run the tests in an isolated D-Bus session and virtual display:

```bash
dbus-run-session --config-file tests/dbus-session.conf -- xvfb-run -a .venv/bin/python -m pytest -q
```

The tests simulate media players and lyric responses; they do not need a
Spotify account or live lyric-provider access.

## Making changes

Keep lyric-provider and artwork requests off the Qt interface thread. Preserve
the checks that discard results from previous songs. Use the session D-Bus for
media information and desktop inhibition, and XDG paths for persistent data.

For behavior changes, run the relevant tests and include a regression test
when it demonstrates an actual failure. For UI changes, also launch the app
in your desktop session and check the tray and `--no-tray` controls.

When reporting a bug, include your distribution, desktop environment, X11 or
Wayland session type, Python version, media player, and steps to reproduce it.
Report missing lyrics with the track title, artist, duration, and selected
sources. Remove API keys and private paths from logs before sharing them.

## Packaging and releases

```bash
./build.sh
./install.sh
```

The installer writes into the current user's local directories. For packaging
checks, set `XDG_DATA_HOME` and `VERSEFLOW_BIN_DIR`
to temporary directories rather than installing into your regular profile.

The GitHub workflow runs the Linux tests and builds an x86_64 portable archive
on Ubuntu 22.04. A `v`-prefixed version tag stamps the application version and
repository, then publishes the archive to GitHub Releases. Build on the oldest
distribution you intend to support and test the resulting archive there.

The download website lives in `docs/`. Preview it with
`python3 -m http.server 4173 --directory docs --bind 127.0.0.1`, then visit
`http://localhost:4173`. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for Netlify
and GitHub Pages hosting. Keep its repository and artifact names consistent
with the application and release workflow.

## License and attribution

Contributions are distributed under the project's GNU GPL v3 license. Keep
the original attribution and dependency notices; see [README credits](README.md#license-and-credits)
and [LICENSE](LICENSE).

Thank you, **[rajbhar-rohit](https://github.com/rajbhar-rohit)**, for creating
**[Constelyric](https://github.com/rajbhar-rohit/Constelyric)** and sharing the
open-source foundation for VerseFlow.
