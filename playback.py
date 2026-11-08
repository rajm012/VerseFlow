"""Keep MPRIS polling independent of network lookups; deliver results on Qt's UI thread."""
import asyncio
import copy
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests
from PyQt6.QtCore import QObject, pyqtSignal

from linux_media import IdleInhibitor, MprisClient
from lyrics_sources import find_lyrics


def load_artwork(url):
    limit = 8 * 1024 * 1024
    try:
        parts = urlsplit(url)
        if parts.scheme == "file" and parts.netloc in ("", "localhost"):
            with Path(unquote(parts.path)).open("rb") as stream:
                data = stream.read(limit + 1)
            return data if len(data) <= limit else None
        if parts.scheme in ("http", "https"):
            with requests.get(url, timeout=4, stream=True) as response:
                response.raise_for_status()
                data = bytearray()
                for chunk in response.iter_content(65536):
                    data.extend(chunk)
                    if len(data) > limit:
                        return None
                return bytes(data)
    except (OSError, requests.RequestException, ValueError):
        pass
    return None


class MediaService(QObject):
    snapshot = pyqtSignal(object)
    searching = pyqtSignal(object)
    lyrics = pyqtSignal(object, object)
    artwork = pyqtSignal(object, object)
    error = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        self._config = {}
        self._revision = 0
        self._lookup_config = None
        self._identity = None
        self.configure(config)

    def configure(self, config):
        updated = copy.deepcopy(dict(config))
        lookup_config = json.dumps([updated.get("sources"), updated.get("musixmatch_key", "")], sort_keys=True)
        with self._lock:
            if lookup_config != self._lookup_config:
                self._revision += 1
                self._lookup_config = lookup_config
            self._config = updated

    def start(self):
        self._thread = threading.Thread(target=self._run, name="verseflow-mpris", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=4)

    def _run(self):
        asyncio.run(self._monitor())

    async def _monitor(self):
        lookup_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="verseflow-lyrics")
        art_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="verseflow-art")
        tasks = set()
        cancellation = None
        art_key = None
        client, inhibitor = None, None

        def spawn(coroutine):
            task = asyncio.create_task(coroutine)
            tasks.add(task)
            task.add_done_callback(tasks.discard)

        try:
            while not self._stop.is_set():
                try:
                    if client is None:
                        client = MprisClient()
                        await client.connect()
                        inhibitor = IdleInhibitor(client)
                    with self._lock:
                        config, revision = self._config, self._revision
                    current = await client.read_current()
                    self.snapshot.emit(current)
                    identity = (current.key, revision) if current else None
                    if identity != self._identity:
                        self._identity = identity
                        if cancellation:
                            cancellation.set()
                        if current:
                            cancellation = threading.Event()
                            self.searching.emit(identity)
                            spawn(self._lookup(identity, current, config, cancellation, lookup_pool))
                    new_art_key = (current.key, current.art_url) if current else None
                    if new_art_key != art_key:
                        art_key = new_art_key
                        if current:
                            spawn(self._artwork(new_art_key, art_pool))
                    await inhibitor.set_enabled(bool(config.get("awake") and config.get("show")
                                                     and current and current.playing))
                except Exception as exc:
                    self.error.emit(f"Cannot read Linux media sessions: {exc}")
                    self.snapshot.emit(None)
                    self._identity = None
                    art_key = None
                    if cancellation:
                        cancellation.set()
                    if client:
                        client.close()
                    client, inhibitor = None, None
                    # Short waits also allow shutdown when the session bus is unavailable.
                    for _ in range(8):
                        if self._stop.is_set():
                            break
                        await asyncio.sleep(0.25)
                await asyncio.sleep(0.25)
        finally:
            if cancellation:
                cancellation.set()
            if inhibitor:
                await inhibitor.set_enabled(False)
            if client:
                client.close()
            for task in tasks:
                task.cancel()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            lookup_pool.shutdown(wait=False, cancel_futures=True)
            art_pool.shutdown(wait=False, cancel_futures=True)

    async def _lookup(self, identity, current, config, cancellation, executor):
        try:
            result = await asyncio.get_running_loop().run_in_executor(
                executor, find_lyrics, current.artist, current.title, current.duration, config, cancellation)
            if not cancellation.is_set() and identity == self._identity:
                self.lyrics.emit(identity, result)
        except Exception as exc:
            if identity == self._identity:
                self.error.emit(f"Lyrics lookup failed: {exc}")
                self.lyrics.emit(identity, None)

    async def _artwork(self, key, executor):
        data = await asyncio.get_running_loop().run_in_executor(executor, load_artwork, key[1])
        if self._identity and key[0] == self._identity[0]:
            self.artwork.emit(key, data)
