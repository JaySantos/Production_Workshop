import math

import pytest

from vectorstore import VectorStore


def test_cosine_similarity_identical_vectors_is_one():
    store = VectorStore()
    vec = [1.0, 2.0, 3.0]
    assert math.isclose(store.cosine_similarity(vec, vec), 1.0)


def test_cosine_similarity_orthogonal_vectors_is_zero():
    store = VectorStore()
    assert math.isclose(store.cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)


def test_cosine_similarity_mismatched_lengths_raises():
    store = VectorStore()
    with pytest.raises(ValueError):
        store.cosine_similarity([1.0, 2.0], [1.0])


def test_add_and_query_returns_top_k_by_score():
    store = VectorStore()
    store.add(
        ids=["a", "b", "c"],
        vectors=[[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]],
        texts=["text a", "text b", "text c"],
    )
    results = store.query([1.0, 0.0], top_k=2)
    # a is identical to the query (cos=1), c is close (cos≈0.994), b is orthogonal (cos=0)
    assert list(results.keys()) == ["a", "c"]


def test_query_raises_on_empty_store():
    store = VectorStore()
    with pytest.raises(ValueError):
        store.query([1.0, 0.0], top_k=1)


def test_save_and_load_round_trip(tmp_path):
    store = VectorStore()
    store.add(["a"], [[1.0, 2.0]], ["hello"])
    path = tmp_path / "store.json"
    store.save(str(path))

    reloaded = VectorStore()
    reloaded.load(str(path))
    assert reloaded.data == store.data
