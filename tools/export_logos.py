"""Export the selected Aurora Wave logo for the app, website, and sharing.

Run with QT_QPA_PLATFORM=offscreen .venv/bin/python tools/export_logos.py.
Uses the project's existing PyQt6 dependency.
"""
import shutil
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parents[1]


def render(source, size):
    renderer = QSvgRenderer(str(source))
    if not renderer.isValid():
        raise ValueError(f"Invalid SVG: {source}")
    output = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    output.fill(Qt.GlobalColor.transparent)
    painter = QPainter(output)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    return output


def save(output, path):
    if not output.save(str(path), "PNG"):
        raise RuntimeError(f"Cannot save {path}")


def main():
    app = QGuiApplication([])
    source = ROOT / "assets" / "logo.svg"
    save(render(source, 256), ROOT / "assets" / "logo.png")
    save(render(source, 1024), ROOT / "assets" / "logo-1024.png")
    shutil.copyfile(source, ROOT / "docs" / "logo.svg")
    print("Updated assets/logo.png, assets/logo-1024.png, and docs/logo.svg")
    app.quit()


if __name__ == "__main__":
    main()
