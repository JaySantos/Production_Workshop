from unittest.mock import Mock, patch

from embeddings import Embedder


def test_embed_returns_list_of_lists():
    fake_model = Mock()
    fake_model.encode.return_value.tolist.return_value = [[0.1, 0.2], [0.3, 0.4]]
    with patch("embeddings.SentenceTransformer", return_value=fake_model):
        embedder = Embedder()
        result = embedder.embed(["a", "b"])
    assert result == [[0.1, 0.2], [0.3, 0.4]]
