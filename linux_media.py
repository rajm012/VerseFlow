"""Linux media sessions and idle inhibition over the user's D-Bus session."""
import asyncio
import re
import time
from dataclasses import dataclass

from dbus_next import Message, MessageType
from dbus_next.aio import MessageBus

MPRIS_PATH = "/org/mpris/MediaPlayer2"
PLAYER = "org.mpris.MediaPlayer2.Player"
PROPERTIES = "org.freedesktop.DBus.Properties"


def normalize_browser_metadata(player, title, artist):
    """Handle browser video titles such as 'Artist - Song' and VEVO/Topic channel names.

    Keep recording qualifiers (live, acoustic, etc.) for the lyrics matcher. Do not split
    ordinary native-player track titles or unrelated titles containing a dash.
    """
    browsers = ("brave", "chromium", "chrome", "google-chrome", "firefox")
    if not any(player.startswith("org.mpris.MediaPlayer2." + browser) for browser in browsers):
        return title, artist
    parts = re.split(r"\s+[-–—]\s+", title, maxsplit=1)
    if len(parts) != 2 or not all(part.strip() for part in parts):
        return title, artist
    candidate, song = (part.strip() for part in parts)

    def channel_name(name):
        name = re.sub(r"\W+", "", name.casefold())
        return re.sub(r"(?:official)?vevo$|official$|topic$", "", name)

    if not artist or channel_name(candidate) == channel_name(artist):
        return song, candidate
    return title, artist


@dataclass(frozen=True)
class PlayerSnapshot:
    player: str
    track_id: str
    title: str
    artist: str
    duration: float
    position: float
    playing: bool
    stamp: float
    art_url: str = ""

    @property
    def key(self):
        return (self.player, self.track_id, self.artist, self.title, self.duration)


class PositionClock:
    """Extrapolate players which only update Position on a seek or status change."""
    def __init__(self):
        self.key = None
        self.raw = None
        self.position = 0.0
        self.stamp = 0.0
        self.playing = False

    def update(self, key, raw, playing, stamp, seeked=False):
        predicted = self.position + (stamp - self.stamp if self.playing else 0)
        if key != self.key:
            position = raw or 0.0
        elif seeked or (raw is not None and raw != self.raw):
            position = raw
        else:
            position = predicted
        self.key, self.raw, self.playing = key, raw, playing
        self.position, self.stamp = max(0.0, position), stamp
        return self.position


class MprisClient:
    def __init__(self):
        self.bus = None
        self.selected = None
        self._players = []
        self._listed_at = -10.0
        self._clocks = {}
        self._seeks = {}

    async def connect(self):
        self.bus = await MessageBus().connect()
        self.bus.add_message_handler(self._signal)
        await self.call("org.freedesktop.DBus", "/org/freedesktop/DBus",
                        "org.freedesktop.DBus", "AddMatch", "s",
                        [f"type='signal',interface='{PLAYER}',member='Seeked',path='{MPRIS_PATH}'"])

    def _signal(self, message):
        if (message.message_type == MessageType.SIGNAL and message.interface == PLAYER
                and message.member == "Seeked" and message.body):
            self._seeks[message.sender] = (max(0, message.body[0]) / 1_000_000, time.monotonic())

    async def call(self, destination, path, interface, member, signature="", body=None):
        reply = await asyncio.wait_for(self.bus.call(Message(
            destination=destination, path=path, interface=interface,
            member=member, signature=signature, body=body or [])), timeout=1.5)
        if reply.message_type == MessageType.ERROR:
            raise RuntimeError(f"{reply.error_name}: {reply.body}")
        return reply

    async def _read(self, name):
        try:
            reply = await self.call(name, MPRIS_PATH, PROPERTIES, "GetAll", "s", [PLAYER])
            props = {k: v.value for k, v in reply.body[0].items()}
            metadata = {k: v.value for k, v in props.get("Metadata", {}).items()}
            title = str(metadata.get("xesam:title") or "").strip()
            status = props.get("PlaybackStatus", "Stopped")
            if not title or status == "Stopped":
                return None
            artists = metadata.get("xesam:artist") or []
            artist = artists if isinstance(artists, str) else ", ".join(str(a) for a in artists)
            title, artist = normalize_browser_metadata(name, title, artist)
            duration = max(0, metadata.get("mpris:length", 0)) / 1_000_000
            track_id = str(metadata.get("mpris:trackid") or "")
            key = (name, track_id, artist, title, duration)
            stamp = time.monotonic()
            raw = max(0, props["Position"]) / 1_000_000 if "Position" in props else None
            seek = self._seeks.pop(reply.sender, None)
            if seek:
                raw = seek[0] + (stamp - seek[1] if status == "Playing" else 0)
            clock = self._clocks.setdefault(name, PositionClock())
            position = clock.update(key, raw, status == "Playing", stamp, seeked=bool(seek))
            if seek:
                # Keep the sampled property as the baseline: some players emit Seeked but
                # leave Position unchanged until a later update.
                clock.raw = max(0, props["Position"]) / 1_000_000 if "Position" in props else None
            if duration:
                position = min(position, duration)
            return PlayerSnapshot(name, track_id, title, artist, duration, position,
                                  status == "Playing", stamp, str(metadata.get("mpris:artUrl") or ""))
        except (RuntimeError, asyncio.TimeoutError, TypeError, ValueError, KeyError):
            return None  # one disappearing or broken player must not hide the others

    async def read_current(self):
        if time.monotonic() - self._listed_at >= 1.0:
            reply = await self.call("org.freedesktop.DBus", "/org/freedesktop/DBus",
                                    "org.freedesktop.DBus", "ListNames")
            self._players = sorted(n for n in reply.body[0] if n.startswith("org.mpris.MediaPlayer2."))
            self._clocks = {n: c for n, c in self._clocks.items() if n in self._players}
            self._listed_at = time.monotonic()
        snapshots = [s for s in await asyncio.gather(*(self._read(n) for n in self._players)) if s]
        if not snapshots:
            self.selected = None
            return None
        # Prefer a playing session; avoid switching between equally active players every poll.
        snapshots.sort(key=lambda s: (not s.playing, s.player != self.selected, s.player))
        self.selected = snapshots[0].player
        return snapshots[0]

    def close(self):
        if self.bus:
            self.bus.disconnect()


class IdleInhibitor:
    """GNOME session inhibition, with the freedesktop ScreenSaver API as fallback."""
    def __init__(self, client):
        self.client = client
        self.token = None
        self.backend = None
        self._enabled = False
        self._retry_at = 0.0

    async def set_enabled(self, enabled):
        self._enabled = enabled
        if not enabled:
            if self.token is not None:
                destination, path, interface, release = self.backend
                try:
                    await self.client.call(destination, path, interface, release, "u", [self.token])
                except (RuntimeError, asyncio.TimeoutError):
                    pass
                self.token, self.backend = None, None
            return
        if self.token is not None or time.monotonic() < self._retry_at:
            return
        for destination, path, interface, method, release, signature, body in (
            ("org.gnome.SessionManager", "/org/gnome/SessionManager", "org.gnome.SessionManager",
             "Inhibit", "Uninhibit", "susu", ["VerseFlow", 0, "Showing synchronized lyrics", 8]),
            ("org.freedesktop.ScreenSaver", "/ScreenSaver", "org.freedesktop.ScreenSaver",
             "Inhibit", "UnInhibit", "ss", ["VerseFlow", "Showing synchronized lyrics"]),
        ):
            try:
                reply = await self.client.call(destination, path, interface, method, signature, body)
                self.token = reply.body[0]
                self.backend = (destination, path, interface, release)
                return
            except (RuntimeError, asyncio.TimeoutError, IndexError):
                continue
        self._retry_at = time.monotonic() + 60
