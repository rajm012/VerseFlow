import asyncio

import pytest
from dbus_next import Variant, PropertyAccess
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, dbus_property, signal

from linux_media import MPRIS_PATH, PLAYER, MprisClient, PositionClock, IdleInhibitor, normalize_browser_metadata


@pytest.mark.parametrize("player,title,artist,expected", [
    ("brave.instance1", "Astrid S - Hurts So Good (Live from Oslo Spektrum)", "AstridSofficialVEVO",
     ("Hurts So Good (Live from Oslo Spektrum)", "Astrid S")),
    ("firefox.instance1", "Artist - Song (Official Video)", "Artist - Topic",
     ("Song (Official Video)", "Artist")),
    ("spotify", "Astrid S - Hurts So Good", "AstridSofficialVEVO",
     ("Astrid S - Hurts So Good", "AstridSofficialVEVO")),
    ("brave.instance1", "Love - Hate", "Other Artist", ("Love - Hate", "Other Artist")),
])
def test_browser_video_metadata(player, title, artist, expected):
    assert normalize_browser_metadata("org.mpris.MediaPlayer2." + player, title, artist) == expected


class FakePlayer(ServiceInterface):
    def __init__(self, title="Test song", status="Playing"):
        super().__init__(PLAYER)
        self.title = title
        self.status = status
        self.position = 10_000_000
        self.track = "/test/track1"

    @dbus_property(access=PropertyAccess.READ)
    def PlaybackStatus(self) -> "s":
        return self.status

    @dbus_property(access=PropertyAccess.READ)
    def Position(self) -> "x":
        return self.position

    @dbus_property(access=PropertyAccess.READ)
    def Metadata(self) -> "a{sv}":
        return {"xesam:title": Variant("s", self.title),
                "xesam:artist": Variant("as", ["First artist", "Second artist"]),
                "mpris:length": Variant("x", 120_000_000),
                "mpris:trackid": Variant("o", self.track),
                "mpris:artUrl": Variant("s", "file:///tmp/album.png")}

    @signal()
    def Seeked(self, position: "x") -> "x":
        return position


@pytest.fixture
async def mpris():
    buses = []
    client = MprisClient()
    await client.connect()

    async def add(name, title="Test song", status="Playing"):
        bus = await MessageBus().connect()
        player = FakePlayer(title, status)
        bus.export(MPRIS_PATH, player)
        await bus.request_name("org.mpris.MediaPlayer2." + name)
        buses.append(bus)
        client._listed_at = -10
        return player, bus

    yield client, add
    client.close()
    for bus in buses:
        bus.disconnect()


async def test_metadata_pause_seek_and_track_change(mpris):
    client, add = mpris
    player, bus = await add("test")
    initial = await client.read_current()
    assert initial.title == "Test song"
    assert initial.artist == "First artist, Second artist"
    assert initial.duration == 120
    assert initial.position == 10
    assert initial.playing
    assert initial.art_url == "file:///tmp/album.png"
    player.status = "Paused"
    player.position = 15_000_000
    paused = await client.read_current()
    assert not paused.playing
    assert paused.position == 15
    assert (await client.read_current()).position == 15
    # Same Position property, explicit Seeked signal: this must still reset the clock.
    player.Seeked(5_000_000)
    await asyncio.sleep(0.02)
    assert (await client.read_current()).position == 5
    assert (await client.read_current()).position == 5
    player.title, player.track, player.position = "Next song", "/test/track2", 0
    changed = await client.read_current()
    assert changed.key != initial.key
    assert changed.position == 0


async def test_player_selection_and_disappearance(mpris):
    client, add = mpris
    paused, _ = await add("aaa", "Paused song", "Paused")
    playing, bus = await add("zzz", "Playing song")
    assert (await client.read_current()).title == "Playing song"
    paused.status = "Playing"
    assert (await client.read_current()).title == "Playing song"  # sticky selection
    playing.status = "Stopped"
    assert (await client.read_current()).title == "Paused song"
    paused.title = ""
    assert await client.read_current() is None
    playing.status = "Playing"
    await bus.release_name("org.mpris.MediaPlayer2.zzz")
    client._listed_at = -10
    assert await client.read_current() is None


def test_position_clock_frozen_missing_seek_pause_and_reset():
    clock = PositionClock()
    assert clock.update("one", 10, True, 100) == 10
    assert clock.update("one", 10, True, 102) == 12
    assert clock.update("one", 10, False, 103) == 13
    assert clock.update("one", 10, False, 105) == 13
    assert clock.update("one", 10, False, 106, seeked=True) == 10
    assert clock.update("two", None, True, 107) == 0
    assert clock.update("two", None, True, 109) == 2
    assert clock.update("two", -2, True, 110, seeked=True) == 0


async def test_inhibitor_fallback_and_release():
    class Client:
        calls = []

        async def call(self, destination, path, interface, member, signature="", body=None):
            self.calls.append((destination, member, body))
            if destination == "org.gnome.SessionManager":
                raise RuntimeError("not GNOME")
            return type("Reply", (), {"body": [42]})()

    client = Client()
    inhibitor = IdleInhibitor(client)
    await inhibitor.set_enabled(True)
    assert inhibitor.token == 42
    await inhibitor.set_enabled(True)
    assert len(client.calls) == 2
    await inhibitor.set_enabled(False)
    assert client.calls[-1][1:] == ("UnInhibit", [42])
    assert inhibitor.token is None
