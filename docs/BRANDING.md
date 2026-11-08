# VerseFlow branding

**VerseFlow** is the name of the Linux project maintained by
[rajm012](https://github.com/rajm012). It combines *verse* and *flow*, matching
lyrics that move with the music. The app and GitHub links use `rajm012/VerseFlow`.

## Aurora Wave logo

![Aurora Wave logo](../assets/logo.png)

**Aurora Wave** is the selected logo for the app, installer, README, and
website. It shows a cyan waveform beneath a pale star on a dark blue tile.
The other logo concepts and comparison sheet have been removed.

- Wave cyan: `#7DD9F2`.
- Star colour: `#DFECFF`.
- Tile gradient: `#132337` to `#173E53`.
- Editable source: [assets/logo.svg](../assets/logo.svg), 512 × 512 view box.
- Desktop and app image: [assets/logo.png](../assets/logo.png), 256 × 256.
- High-resolution export: [assets/logo-1024.png](../assets/logo-1024.png), 1024 × 1024.
- GitHub Pages image: [docs/logo.svg](logo.svg).

The SVG has no font dependencies. The PNG exports preserve transparency
outside the rounded tile.

## Exporting the logo

Edit `assets/logo.svg`, then run from the repository root:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python tools/export_logos.py
```

The exporter refreshes the app icon, high-resolution PNG, and website SVG
using the existing PyQt6 dependency. It exports only the selected design.
Rebuild installed bundles with `./build.sh` and `./install.sh` to update
their icons.

## Credits

The original vector logo is distributed with the project's GNU GPL v3 license.
The original project's authorship remains acknowledged in
[README credits](../README.md#license-and-credits).

Thank you, **[rajbhar-rohit](https://github.com/rajbhar-rohit)**, for creating
**[Constelyric](https://github.com/rajbhar-rohit/Constelyric)** and sharing the
open-source foundation for this Linux project.
