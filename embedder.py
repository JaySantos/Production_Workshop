"""Create embeddings using the specified Transformer."""

from sentence_transformers import SentenceTransformer


class Embedder:
    """Create embeddings using the specified Transformer."""

    def __init__(self):
        """Define the Transformer to be used."""
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Invoke the encode method of the Transformer."""
        numpy_array = self.model.encode(texts, normalize_embeddings=True)
        return numpy_array.tolist()
