import asyncio
import threading
import time

import playback
from linux_media import PlayerSnapshot
from lyrics_sources import Line, Result


async def test_slow_lookup_does_not_block_polling_and_old_results_are_discarded(monkeypatch, qt_app):
    release = threading.Event()
    calls = []
    title = ["First"]

    class Client:
        selected = None

        async def connect(self):
            pass

        async def read_current(self):
            return PlayerSnapshot("test", "/" + title[0], title[0], "Artist", 120,
                                  len(snapshots), True, time.monotonic())

        def close(self):
            pass

    class Inhibitor:
        def __init__(self, client):
            pass

        async def set_enabled(self, enabled):
            pass

    def lookup(artist, song, duration, config, cancel):
        calls.append(song)
        if song == "First":
            release.wait(timeout=3)
        return Result([Line(0, 1, [(song, 0, 1)])], True, song)

    monkeypatch.setattr(playback, "MprisClient", Client)
    monkeypatch.setattr(playback, "IdleInhibitor", Inhibitor)
    monkeypatch.setattr(playback, "find_lyrics", lookup)
    snapshots, results = [], []
    service = playback.MediaService({"awake": False, "show": True})
    service.snapshot.connect(snapshots.append)
    service.lyrics.connect(lambda key, result: results.append(result.source))
    monitor = asyncio.create_task(service._monitor())
    try:
        await asyncio.sleep(0.6)
        assert len(snapshots) >= 3
        assert not results
        assert calls == ["First"]
        title[0] = "Second"
        await asyncio.sleep(0.3)
        release.set()
        await asyncio.sleep(0.3)
        assert results == ["Second"]
        assert snapshots[-1].title == "Second"
    finally:
        release.set()
        service._stop.set()
        await asyncio.wait_for(monitor, timeout=2)
