<p align="center"><img src="assets/logo.png" width="112" alt="VerseFlow logo"></p>

# VerseFlow

**Animated, synchronized lyrics for your Linux desktop.** Maintained by
[rajm012](https://github.com/rajm012), VerseFlow follows your music through
MPRIS over the session D-Bus and displays lyrics with PyQt6.

[Website](https://verseflow-linux.netlify.app/) ·
[Source](https://github.com/rajm012/VerseFlow) ·
[Releases](https://github.com/rajm012/VerseFlow/releases) ·
[Report an issue](https://github.com/rajm012/VerseFlow/issues)

VerseFlow is a Linux adaptation of the open-source
[Constelyric](https://github.com/rajbhar-rohit/Constelyric) project.
The name combines **verse** with **flow**, reflecting lyrics that move in sync
with your music.

## Features

- **Stack:** previous, current, and upcoming lines with karaoke highlighting.
- **Focus:** one line at a time, with words floating into place.
- **Constellation:** fullscreen lyrics connected like stars on a night sky.
- Album-art colours or your own lyric, highlight, and secondary colours.
- Configurable lyric sources, with word timing preferred when available.
- Optional desktop idle inhibition while music plays and lyrics are visible.
- Tray controls, a regular control window, and single-instance activation.

Spotify, VLC, and other players work when they publish MPRIS metadata.
Browser playback depends on the browser and website: generic media titles
cannot reliably be matched to songs.

## Run from source

You need Python 3.10 or newer, a graphical Linux session, and internet access
for lyric lookups. On Ubuntu/Debian:

```bash
sudo apt install python3-venv libxcb-cursor0 libxkbcommon-x11-0
git clone https://github.com/rajm012/VerseFlow.git
cd VerseFlow
./setup.sh
./run.sh
```

For an existing checkout, run `./setup.sh` and `./run.sh` from its directory.
`setup.sh` creates a local `.venv` and installs the Python dependencies.

The controls open at launch. Click the tray icon to reopen them, or launch a
second copy to bring the existing panel forward. On desktops without a tray,
the controls use a regular window; closing it exits the app.

```bash
./run.sh --no-tray                 # regular control window
./run.sh --no-overlay              # start with lyrics hidden
./run.sh --style Constellation     # fullscreen; Escape returns to Stack
./run.sh --version
```

The first desktop target is **Ubuntu/GNOME on X11**, using the primary monitor.
On Wayland, fullscreen is an ordinary application window; overlay placement,
click-through behaviour, and stacking depend on the compositor. Full Wayland
parity and other desktop environments still need testing.

## Lyrics and settings

Use **Lyrics sources → Choose…** to enable, disable, or reorder providers.

| Source | Available timing |
| --- | --- |
| lrc.red | Word |
| BiniLyrics | Word, Apple-style TTML |
| LyricsPlus | Word or line |
| KuGou | Word KRC or line LRC |
| BetterLyrics | Word TTML |
| Musixmatch | Word or line; your API key required, disabled by default |
| LRCLIB | Line |

The first word-timed result wins; otherwise the first line-timed result is
used. Word timing estimated from line-only lyrics may differ from the vocals.
Provider availability and coverage vary.

Settings are stored in `$XDG_CONFIG_HOME/verseflow/settings.json`, normally
`~/.config/verseflow/settings.json`. If the new file is absent, existing Linux
settings are read from `~/.config/versesky/settings.json`, then
`~/.config/constelyric/settings.json`. Future saves use the VerseFlow directory.
Lyrics and failure history are cached
in memory only. Supply a Musixmatch key in the controls or through
`MUSIXMATCH_API_KEY`; a key entered in the controls is saved in the settings file.

Lyric requests send the track title, artist, and supported duration to enabled
providers. Artwork is read from the local file or URL supplied by the player.
Update checks contact GitHub Releases for `rajm012/VerseFlow` at launch and
every six hours, and offer matching Linux artifacts. Lyrics belong to their
respective rights holders.

## Build and install

```bash
./setup.sh
./build.sh
./install.sh
```

The executable is `dist/VerseFlow/VerseFlow`. The portable archive is
`dist/VerseFlow-linux-<architecture>-<version>.tar.gz`; it includes the license,
README with upstream credits, and a per-user installer. Override the build Python with
`VERSEFLOW_PYTHON`.

For a downloaded release, extract the archive, enter the extracted directory,
and run `./install.sh`. The installer needs no administrator rights and creates:

- `~/.local/bin/verseflow` — launcher; override with `VERSEFLOW_BIN_DIR`.
- `$XDG_DATA_HOME/verseflow/` — application, normally `~/.local/share/verseflow/`.
- `$XDG_DATA_HOME/applications/verseflow.desktop` — applications-menu entry.
- `$XDG_DATA_HOME/icons/hicolor/256x256/apps/verseflow.png` — desktop icon.

Installation does not enable automatic startup. To uninstall, remove those
files and directories; remove `~/.config/verseflow/` separately to delete
settings. Use your configured XDG paths if they differ from defaults.

Portable bundles inherit their build host's system-library requirements.
Builds run on the maintainer's local Ubuntu 24.04 x86_64 runner. Build and test
on the oldest distribution you plan to support; compatibility with older
distributions is not established by a successful local build. Other
architectures require their own build.

Release `v1.1.0` uses application version `1.1.0`. The self-hosted workflow
tests and builds locally, then uploads tagged archives directly to GitHub
Releases. See [docs/RELEASING.md](docs/RELEASING.md) for local runner setup and
the command to rebuild an existing release without Actions artifact storage.

## Development and branding

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
# Ubuntu/Debian: sudo apt install dbus xvfb xauth
dbus-run-session --config-file tests/dbus-session.conf -- xvfb-run -a .venv/bin/python -m pytest -q
```

Tests cover simulated MPRIS players, pause and seek handling, stale and slow
lyric requests, caching, Linux release selection, all three displays, and
controls without a tray. See [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the code layout and release setup.

The selected **Aurora Wave** logo has an [editable SVG source](assets/logo.svg)
and a [1024 px PNG export](assets/logo-1024.png).
See [docs/BRANDING.md](docs/BRANDING.md) for its palette and export instructions.

## Website

The live website is **[verseflow-linux.netlify.app](https://verseflow-linux.netlify.app/)**.
Its source lives in `docs/` and includes an interactive lyric
preview, Linux installation instructions, and links to matching GitHub release
archives. It uses the Aurora Wave logo and a cyan-and-mint palette.

Preview it locally:

```bash
python3 -m http.server 4173 --directory docs --bind 127.0.0.1
```

Open `http://localhost:4173`. To host it, connect this repository to Netlify;
the root `netlify.toml` publishes the static site without building the desktop
app. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the complete steps and a
manual drag-and-drop option.

## License and credits

GNU GPL v3; see [LICENSE](LICENSE).
The original project supplies the foundation for the animated displays and
lyric integrations. VerseFlow's Linux adaptation and maintenance are by
[rajm012](https://github.com/rajm012).

Thank you, **[rajbhar-rohit](https://github.com/rajbhar-rohit)**, for creating
**[Constelyric](https://github.com/rajbhar-rohit/Constelyric)** and sharing it
as open source, making VerseFlow possible.
