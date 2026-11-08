# Host VerseFlow on Netlify

The live website is **[https://verseflow-linux.netlify.app/](https://verseflow-linux.netlify.app/)**.
Its Netlify project name is `verseflow-linux`.

The website is in `docs/`. It is plain HTML, CSS, and JavaScript, with the Aurora
logo and locally hosted fonts. It needs no website build step, server, API key,
or package installation. The repository's Python requirements and `build.sh`
belong to the Linux desktop application.

## Connect your GitHub repository

1. Push this project, including `docs/` and `netlify.toml`, to
   [rajm012/VerseFlow](https://github.com/rajm012/VerseFlow) on GitHub.
2. Sign in at [Netlify](https://app.netlify.com/).
3. Choose **Add new project → Import an existing project**, then **GitHub**.
4. Authorize access to your repository and select `rajm012/VerseFlow`.
5. Use these settings. The root `netlify.toml` already supplies the directory
   and build settings:

   | Setting | Value |
   | --- | --- |
   | Production branch | `main` |
   | Framework | No framework / Other |
   | Base directory | `docs` |
   | Build command | Leave empty |
   | Publish directory | `.` |

   The publish directory is relative to the base directory, so `.` here means
   the contents of `docs/`. Using `docs` as the base also keeps the website
   deployment separate from the desktop app's Python dependencies. Leave any
   package-directory setting empty.
6. Deploy the project. Netlify assigns a `*.netlify.app` URL and provides HTTPS.
7. The current project uses the name `verseflow-linux`, giving the live address
   `https://verseflow-linux.netlify.app/`. Keep that name when updating this site.

Future pushes to `main` redeploy the site automatically. Pull requests can
receive Netlify Deploy Previews. GitHub Releases and Netlify website deployments
are separate: the website downloads app archives from GitHub.

## Quick manual deployment

For a first preview, sign in and open [Netlify Drop](https://app.netlify.com/drop).
Drag the **`docs` folder itself** into the drop area. Its root contains
`index.html`, `styles.css`, `script.js`, `logo.svg`, and `fonts/`.

To update that same site, open its **Deploys** page and drop the updated `docs`
folder into the deploy dropzone. Manual deployment does not connect GitHub for
automatic updates; import the repository when you want continuous deployment.

## Preview locally

From the repository root:

```bash
python3 -m http.server 4173 --directory docs --bind 127.0.0.1
```

Open [http://localhost:4173](http://localhost:4173). Press Ctrl+C in the terminal
to stop the preview server. The Python server is only for local preview;
Netlify serves the uploaded static files directly.

## Downloads and maintenance

- `REPO` in `docs/script.js` is set to `rajm012/VerseFlow`. Update it along with
  the HTML links if your repository name changes.
- The website queries GitHub's latest release and offers only a matching
  `VerseFlow-linux-<architecture>-<version>.tar.gz` archive. The default is
  x86_64; the portable-install tab also lets users select ARM64.
- Without a matching published archive, or if GitHub cannot be reached, the
  main button goes to source installation and the portable tab links to
  GitHub Releases. Locally building the app does not publish a GitHub Release.
- Keep the logo at `docs/logo.svg`; it must be inside the published folder.
  Run `tools/export_logos.py` after changing `assets/logo.svg`.
- The fonts' redistribution notices are included under `docs/fonts/`.
- The same static folder can also be hosted with GitHub Pages using
  `main` → `/docs`.

See Netlify's official [build-settings guide](https://docs.netlify.com/build/configure-builds/overview/)
and [deployment guide](https://docs.netlify.com/deploy/create-deploys/) for the
current dashboard options.

Thank you, **[rajbhar-rohit](https://github.com/rajbhar-rohit)**, for creating
**[Constelyric](https://github.com/rajbhar-rohit/Constelyric)** and sharing the
open-source foundation for VerseFlow.
