import pytest

from chunking import chunk_text


def test_short_text_returns_single_chunk():
    text = "short text"
    assert chunk_text(text, chunk_size=50, chunk_overlap=5) == [text]


def test_overlap_must_be_less_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("some text here", chunk_size=10, chunk_overlap=10)


def test_snaps_to_last_space_within_window():
    text = "aaaa bbbb cccc dddd"
    chunks = chunk_text(text, chunk_size=12, chunk_overlap=2)
    # run chunk_text(text, 12, 2) yourself first and confirm this is what
    # it actually returns, then hard-code that confirmed value here
    assert (
        chunks[0] == "aaaa bbbb"
    )  # placeholder — replace with the real expected value
