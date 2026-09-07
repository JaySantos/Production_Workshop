# from unittest.mock import Mock, patch

# import pytest

# import query
# from query import build_prompt


# def test_main_prints_answer_and_sources(monkeypatch, capsys):
#     monkeypatch.setattr("sys.argv", ["query.py", "does this support REST APIs?"])

#     fake_store = Mock()
#     fake_store.query.return_value = {
#         "docs/faq.md::0": {"text": "yes, REST APIs are supported"}
#     }

#     fake_embedder = Mock()
#     fake_embedder.embed.return_value = [[0.1, 0.2, 0.3]]

#     fake_generation = Mock()
#     fake_generation.generate.return_value = "Yes, REST APIs are supported."

#     with (
#         patch("query.VectorStore", return_value=fake_store),
#         patch("query.Embedder", return_value=fake_embedder),
#         patch("query.Generation", return_value=fake_generation),
#     ):
#         query.main()

#     captured = capsys.readouterr()
#     assert "Yes, REST APIs are supported." in captured.out
#     assert "docs/faq.md::0" in captured.out
#     fake_store.load.assert_called_once()


# def test_build_prompt_raises_on_empty_question():
#     with pytest.raises(ValueError):
#         build_prompt("", {"a::0": {"text": "something"}})


# def test_build_prompt_raises_on_empty_chunks():
#     with pytest.raises(ValueError):
#         build_prompt("a question", {})


# def test_build_prompt_includes_question_and_context():
#     result = build_prompt("what is X?", {"a::0": {"text": "X is a thing"}})
#     assert "<question>what is X?</question>" in result
#     assert "X is a thing" in result

from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from query import app

client = TestClient(app)


def test_read_main():
    fake_store = Mock()
    fake_store.query.return_value = {
        "docs/faq.md::0": {"text": "yes, REST APIs are supported"}
    }

    fake_embedder = Mock()
    fake_embedder.embed.return_value = [[0.1, 0.2, 0.3]]

    fake_generation = Mock()
    fake_generation.generate.return_value = "Yes, REST APIs are supported."

    with (
        patch("query.VectorStore", return_value=fake_store),
        patch("query.Embedder", return_value=fake_embedder),
        patch("query.Generation", return_value=fake_generation),
        client,
    ):
        response = client.post("/query", params={"q": "does this support REST APIs?"})
    assert response.status_code == 200
    assert response.json() == {
        "answer": "Yes, REST APIs are supported.",
        "sources": ["docs/faq.md::0"],
    }
