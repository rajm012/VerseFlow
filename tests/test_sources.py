import threading

import pytest

import lyrics_sources as sources


@pytest.fixture
def registry(monkeypatch):
    calls = []

    def provider(name, word):
        def get(artist, title, duration, cfg):
            calls.append((name, duration))
            return sources.Result([sources.Line(0, 2, [("hello", 0, 1), ("world", 1, 2)])], word, name)
        return get

    monkeypatch.setattr(sources, "REGISTRY", {"line": provider("line", False), "word": provider("word", True)})
    monkeypatch.setattr(sources, "INFO", {"line": ("line", ""), "word": ("word", "")})
    monkeypatch.setattr(sources, "DEFAULT_ORDER", ["line", "word"])
    monkeypatch.setattr(sources, "_CACHE", {})
    monkeypatch.setattr(sources, "_FAILS", {})
    return calls


def config(line=True, word=True):
    return {"sources": [{"id": "line", "on": line}, {"id": "word", "on": word}]}


def test_prefers_word_timing_and_caches_identical_queries(registry):
    result = sources.find_lyrics("Artist", "Title", 120, config())
    assert result.source == "word"
    assert sources.find_lyrics("Artist", "Title", 120, config()) is result
    assert len(registry) == 2


def test_cache_respects_disabled_sources_duration_and_credentials(registry):
    sources.find_lyrics("Artist", "Title", 120, config())
    assert sources.find_lyrics("Artist", "Title", 120, config(word=False)).source == "line"
    assert sources.find_lyrics("Artist", "Title", 120, config(False, False)) is None
    sources.find_lyrics("Artist", "Title", 130, config())
    assert ("word", 130) in registry
    before = len(registry)
    sources.find_lyrics("Artist", "Title", 130, dict(config(), musixmatch_key="new-key"))
    assert len(registry) > before


def test_cancelled_song_stops_before_next_provider(registry, monkeypatch):
    cancel = threading.Event()
    original = sources.REGISTRY["line"]

    def first(*args):
        result = original(*args)
        cancel.set()
        return result

    monkeypatch.setitem(sources.REGISTRY, "line", first)
    assert sources.find_lyrics("Artist", "Title", 120, config(), cancel) is None
    assert registry == [("line", 120)]
    assert not sources._CACHE


def test_lrc_estimated_words_stay_within_line():
    lines = sources.build_lines("[00:10.00]Hello world\n[00:12.00]Next line")
    assert lines[0].start == 10
    assert lines[0].end == 12
    assert [w[0] for w in lines[0].words] == ["Hello", "world"]
    assert lines[0].words[0][1] < lines[0].words[0][2] <= lines[0].words[1][1]
    assert lines[0].words[-1][2] <= lines[0].end


def test_ttml_word_timings_and_background_vocals():
    lines, word_synced = sources.parse_ttml('''
    <tt xmlns="http://www.w3.org/ns/ttml" xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
      <body><div><p begin="10s" end="12s"><span begin="10s" end="11s">Hello </span><span begin="11s" end="12s">world</span><span ttm:role="x-bg" begin="10s" end="12s">background</span></p></div></body>
    </tt>''')
    assert word_synced
    assert lines[0].words == [("Hello", 10, 11), ("world", 11, 12)]


def test_binilyrics_skips_wrong_recording_duration(monkeypatch):
    fetched = []
    candidates = [{"duration": 208, "lyricsUrl": "https://example.org/studio.ttml"},
                  {"duration": 284, "lyricsUrl": "https://example.org/live.ttml"}]

    class Response:
        ok = True
        text = '<tt><body><p begin="10s" end="12s"><span begin="10s" end="12s">Hello</span></p></body></tt>'

        def json(self):
            return {"results": candidates}

    def get(url, params=None):
        fetched.append(url)
        return Response()

    monkeypatch.setattr(sources, "_get", get)
    result = sources.src_binilyrics("Astrid S", "Hurts So Good (Live)", 284.101, {})
    assert result and result.source == "BiniLyrics"
    assert "https://example.org/live.ttml" in fetched
    assert "https://example.org/studio.ttml" not in fetched
    candidates.pop()
    assert sources.src_binilyrics("Astrid S", "Hurts So Good (Live)", 284.101, {}) is None
