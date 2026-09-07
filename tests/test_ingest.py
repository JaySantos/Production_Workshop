# tests/test_ingest.py
from unittest.mock import Mock

import ingest


def test_main_chunks_files_and_calls_add_and_save(tmp_path):
    doc = tmp_path / "sample.md"
    doc.write_text(
        "This is a short sample document for testing ingest.", encoding="utf-8"
    )

    fake_embedder = Mock()
    fake_embedder.embed.return_value = [[0.1, 0.2, 0.3]]
    fake_store = Mock()

    ingest.main(folder=str(tmp_path), embedder=fake_embedder, vector_store=fake_store)

    fake_embedder.embed.assert_called_once()
    fake_store.add.assert_called_once()
    fake_store.save.assert_called_once()
