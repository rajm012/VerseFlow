# VerseFlow development

VerseFlow is maintained by [rajm012](https://github.com/rajm012) at
[rajm012/VerseFlow](https://github.com/rajm012/VerseFlow).
Start with the setup and test commands in [CONTRIBUTING.md](../CONTRIBUTING.md).

## Code layout

| File | Responsibility |
| --- | --- |
| `verseflow.py` | Qt displays, controls, settings, single instance, update checks |
| `linux_media.py` | MPRIS metadata, playback clock, desktop idle inhibition |
| `playback.py` | Background media polling, lyric requests, artwork loading |
| `lyrics_sources.py` | Provider integrations, timing parsers, source preferences, cache |
| `release_assets.py` | Matching Linux release artifacts to the current architecture |
| `setup.sh`, `run.sh` | Local virtual environment and source launcher |
| `build.sh`, `install.sh` | Portable Linux bundle and per-user installation |
| `packaging/verseflow.desktop` | Linux applications-menu metadata |
| `tests/` | Isolated D-Bus, playback, lyric-provider, and Qt checks |
| `assets/logo.svg`, `assets/logo.png`, `assets/logo-1024.png` | Aurora Wave source and PNG exports |
| `tools/export_logos.py` | Export the Aurora Wave app icon and high-resolution PNG using Qt |
| `docs/index.html`, `docs/styles.css`, `docs/script.js` | Static download website and interactive lyric demo |
| `netlify.toml`, `docs/DEPLOYMENT.md` | Netlify hosting configuration and instructions |
| `docs/RELEASING.md` | Local runner setup and direct GitHub Release uploads |

## Repository and releases

The app and website use `rajm012/VerseFlow` as their repository target. If you
publish under a different repository name, update `GITHUB_REPO` in
`verseflow.py`, `REPO` in `docs/script.js`, and the HTML and documentation links.
The local checkout's remote is configured separately with Git.

The workflow in `.github/workflows/release.yml` uses the local runner with
labels `self-hosted`, `linux`, `x64`, and `verseflow`. It tests and builds pushes
to `main` and `v`-prefixed tags, plus manual runs. Tagged builds stamp the app
version and repository, then upload the exact archive directly to GitHub
Releases. There is no Actions artifact upload or GitHub cache step. A manual
run can specify an existing `release_tag`; checkout then builds that tag.
See [RELEASING.md](RELEASING.md). The current application version is `1.1.0`.

The website is live at [verseflow-linux.netlify.app](https://verseflow-linux.netlify.app/)
and uses the root `netlify.toml`; see
[DEPLOYMENT.md](DEPLOYMENT.md). It can also be served with GitHub Pages from
`main` → `/docs`. The website uses `docs/logo.svg` and self-hosted fonts so all
visual assets are inside the published folder. It falls back to source
installation instructions when no matching Linux archive exists.

## Check a portable bundle

Build with `./build.sh`, extract the archive into a temporary directory, and
run `./install.sh` inside the extracted folder. Set `XDG_DATA_HOME` and
`VERSEFLOW_BIN_DIR` to temporary directories to avoid touching your normal app
installation. Check the launcher, `.desktop` entry, icon, license, and credits.

The local release runner uses Ubuntu 24.04 on Linux x86_64. Other Linux
architectures can be built locally; distro and compositor coverage should be
reported only after testing those environments.

## Settings compatibility

New settings use `$XDG_CONFIG_HOME/verseflow/settings.json`. When that file is
absent, the application first checks `$XDG_CONFIG_HOME/versesky/settings.json`,
then `$XDG_CONFIG_HOME/constelyric/settings.json`. Saving writes to the new path
and leaves previous files available to older versions.

## Attribution

Keep [LICENSE](../LICENSE) and [README credits](../README.md#license-and-credits) in redistributed
bundles. See [BRANDING.md](BRANDING.md) for the logo assets and selection steps.

Thank you, **[rajbhar-rohit](https://github.com/rajbhar-rohit)**, for creating
**[Constelyric](https://github.com/rajbhar-rohit/Constelyric)** and sharing the
open-source foundation for VerseFlow.
