import time

import pytest
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QKeyEvent

import verseflow as app
from linux_media import PlayerSnapshot
from lyrics_sources import Line, Result
from playback import load_artwork


@pytest.fixture
def song(monkeypatch, tmp_path, qt_app):
    state = app.State()
    monkeypatch.setattr(app, "STATE", state)
    settings = dict(app.Settings.DEFAULTS)

    class Config(dict):
        def save(self):
            pass

    monkeypatch.setattr(app, "S", Config(settings))
    current = PlayerSnapshot("player", "/song", "Test song", "Artist", 120, 10.5, True, time.monotonic())
    state.update_snapshot(current)
    identity = (current.key, 1)
    state.update_search(identity)
    state.update_lyrics(identity, Result([
        Line(8, 10, [("Past", 8, 9)]),
        Line(10, 12, [("Hello", 10, 11), ("world", 11, 12)]),
        Line(12, 14, [("Next", 12, 14)]),
    ], True, "Test provider"))
    return state


@pytest.mark.parametrize("style", ["Stack", "Focus", "Constellation"])
def test_styles_render_and_fullscreen_escape(song, qt_app, style):
    app.S["style"] = style
    overlay = app.Overlay()
    try:
        qt_app.processEvents()
        pixmap = overlay.grab()
        assert not pixmap.isNull()
        assert overlay.isVisible()
        if style == "Constellation":
            assert overlay.nodes
            overlay.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier))
            assert app.S["style"] == "Stack"
    finally:
        overlay.close()
        overlay.deleteLater()


def test_stale_lyrics_are_ignored_and_source_change_refreshes(song):
    original = song.lines
    song.update_lyrics((song.key, 0), None)
    assert song.lines is original
    song.update_search((song.key, 2))
    assert song.status == "searching"
    song.update_lyrics((song.key, 1), None)
    assert song.status == "searching"
    song.update_lyrics((song.key, 2), None)
    assert song.status == "none"


def test_controls_remain_visible_without_tray(song, qt_app):
    overlay = app.Overlay()
    panel = app.Panel(overlay, qt_app, standalone=True)
    try:
        panel.toggle()
        qt_app.processEvents()
        panel.event(QEvent(QEvent.Type.WindowDeactivate))
        assert panel.isVisible()
        assert "Test provider" in panel.t_status.text()
        assert not panel.grab().isNull()
        panel._open_sources()
        qt_app.processEvents()
        panel.sources.hide()
        assert panel.isVisible()
    finally:
        panel.hide()
        panel.deleteLater()
        overlay.close()
        overlay.deleteLater()


def test_artwork_file_urls_with_spaces(tmp_path):
    path = tmp_path / "album art.png"
    path.write_bytes(b"test image bytes")
    assert load_artwork(path.as_uri()) == path.read_bytes()
    assert load_artwork("file://remote-host/image.png") is None
    assert load_artwork("data:image/png;base64,test") is None
    assert load_artwork("https://[invalid/image.png") is None


@pytest.mark.parametrize("previous_name", ["versesky", "constelyric"])
def test_renamed_settings_preserve_previous_linux_preferences(monkeypatch, tmp_path, previous_name):
    previous = tmp_path / previous_name / "settings.json"
    current = tmp_path / "verseflow" / "settings.json"
    previous.parent.mkdir()
    previous.write_text('{"style": "Focus", "awake": false}')
    monkeypatch.setattr(app.Settings, "PATH", current)
    monkeypatch.setattr(app.Settings, "_PREVIOUS", (previous,))
    monkeypatch.setattr(app, "MEDIA", None)
    settings = app.Settings()
    assert settings["style"] == "Focus"
    assert settings["awake"] is False
    settings.save()
    assert current.exists()
    assert previous.exists()
    current.write_text('{"style": "Stack"}')
    assert app.Settings()["style"] == "Stack"


def test_latest_previous_settings_take_precedence(monkeypatch, tmp_path):
    previous = (tmp_path / "versesky.json", tmp_path / "constelyric.json")
    previous[0].write_text('{"style": "Focus"}')
    previous[1].write_text('{"style": "Constellation"}')
    monkeypatch.setattr(app.Settings, "PATH", tmp_path / "verseflow.json")
    monkeypatch.setattr(app.Settings, "_PREVIOUS", previous)
    assert app.Settings()["style"] == "Focus"


def test_selected_logo_is_loaded_at_tray_and_panel_sizes(qt_app):
    from pathlib import Path
    from PyQt6.QtGui import QImage

    selected = QImage(str(Path(app.__file__).parent / "assets" / "logo.png"))
    assert not selected.isNull()
    actual = app.logo_pixmap(256).toImage()
    assert actual.pixelColor(128, 128) == selected.pixelColor(128, 128)
    for size in (16, 32, 64):
        icon = app.logo_pixmap(size).toImage()
        assert icon.width() == size
        assert icon.pixelColor(size // 2, size // 2).alpha() > 0
