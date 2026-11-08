# Build and publish VerseFlow locally

Website: [verseflow-linux.netlify.app](https://verseflow-linux.netlify.app/).
Releases: [rajm012/VerseFlow](https://github.com/rajm012/VerseFlow/releases).
The current release is `v1.1.0`, with application version `1.1.0`.

The workflow builds on the maintainer's Ubuntu 24.04 x86_64 PC. GitHub queues
the job and stores its logs; the local runner executes the tests and PyInstaller
build. Tagged archives upload directly to GitHub Releases. The workflow does
not use GitHub-hosted runner minutes, Actions artifact uploads, or Actions
cache uploads. The website remains hosted independently on Netlify.

## Local runner

The registered runner is named `rajm012`. Its directory is
`~/Desktop/actions-runner`, and its systemd service is
`actions.runner.rajm012-VerseFlow.rajm012.service`. Jobs run in its `_work`
directory using the repository commit or release tag selected by the workflow.

```bash
sudo systemctl start actions.runner.rajm012-VerseFlow.rajm012.service
systemctl status actions.runner.rajm012-VerseFlow.rajm012.service
```

The machine must stay awake and online for jobs to run. The service is enabled
at boot. The workflow requires the runner labels `self-hosted`, `linux`, `x64`,
and `verseflow`, plus Python 3.10+, `gh`, D-Bus, and Xvfb. Install dependencies
once on the PC rather than using `sudo apt` inside each job:

```bash
sudo apt install python3-venv xvfb xauth dbus-x11 libxcb-cursor0 libxkbcommon-x11-0
```

If the runner needs reinstalling, use **GitHub repository → Settings → Actions
→ Runners → New self-hosted runner**. Download the official Linux x64 archive,
verify its GitHub release SHA-256 digest, extract it into the runner directory,
and follow GitHub's registration commands as the normal user. Registration
tokens are temporary; do not commit them or the runner's credentials.

Pull-request triggers are omitted because this runner executes code on a
personal PC. Builds run only for `main` pushes, release tags, and manual runs.

## Rebuild an existing release

From this PC, while signed in with GitHub CLI:

```bash
gh workflow run release.yml --repo rajm012/VerseFlow --ref main -f release_tag=v1.1.0
gh run list --repo rajm012/VerseFlow --workflow release.yml --limit 5
```

The workflow checks out the existing tag, stamps the version without its `v`
prefix, runs the tests, builds the archive, and uploads it to that release.
Rebuilding replaces the asset with the same filename. A manual run with no
`release_tag` tests and builds `main` without publishing a release.

## Publish a new version

Update `APP_VERSION` in `verseflow.py`, commit the changes, and push `main`.
Then create and push a matching version tag, for example:

```bash
git tag v1.1.1
git push origin v1.1.1
```

Use a new version for changed application code; keep published tags pointing
to their original commits. The tagged workflow uploads
`VerseFlow-linux-x86_64-1.1.1.tar.gz`. The website automatically reads the latest
GitHub Release and offers its matching Linux archive.

## Build and upload without invoking Actions

For a manual build of the current checkout:

```bash
./setup.sh
.venv/bin/python -m pip install -r requirements-dev.txt
dbus-run-session --config-file tests/dbus-session.conf -- xvfb-run -a .venv/bin/python -m pytest -q
./build.sh
```

Before uploading, make sure the archive was built from the intended tagged
commit and its application version matches that tag. For `v1.1.0`:

```bash
gh release upload v1.1.0 dist/VerseFlow-linux-x86_64-1.1.0.tar.gz --repo rajm012/VerseFlow --clobber
```

## Verify the published download

Download the archive into an empty folder, extract it, and enter its directory.
Run `./install.sh`, then `verseflow --version` and `verseflow --no-tray`.
For an isolated installation check, override `XDG_DATA_HOME` and
`VERSEFLOW_BIN_DIR` with temporary directories.

Portable bundles inherit the build host's system-library requirements. A
successful Ubuntu 24.04 check does not establish support for older Linux
distributions or every Wayland compositor.

Thank you, **[rajbhar-rohit](https://github.com/rajbhar-rohit)**, for creating
**[Constelyric](https://github.com/rajbhar-rohit/Constelyric)** and sharing the
open-source foundation for VerseFlow.
