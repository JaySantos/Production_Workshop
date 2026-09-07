"""Create the JSON file containing the embedding of the documentation chunks."""

import json
import math

import fileoperations


class VectorStore:
    """Create the JSON file containing the embedding of the documentation chunks."""

    def __init__(self):
        """Init function."""
        self.data = {}

    @staticmethod
    def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """Calculate the cosine similarity between two vectors."""
        if len(vec_a) != len(vec_b):
            raise ValueError("Vectors must be the same length")
        dot_product = sum(x * y for x, y in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(x * x for x in vec_a))
        mag_b = math.sqrt(sum(y * y for y in vec_b))
        magnitude = mag_a * mag_b
        if magnitude == 0:
            raise ValueError("Magnitude = 0")
        return dot_product / magnitude

    def add(self, ids: list[str], vectors: list[list[float]], texts: list[str]) -> None:
        """Add the IDs, arrays of vectors, and raw texts to the data dictionary."""
        for i, current_id in enumerate(ids):
            self.data[current_id] = {"vector": vectors[i], "text": texts[i]}

    def query(self, query_vector: list[float], top_k: int) -> dict:
        """Run cosine_similarity between the query_vector and all vectors in self.data.

        Returns the top_k self.data entries by cosine_similarity
        """
        if len(self.data) == 0:
            raise ValueError("No data to query")
        scores = {}
        for current_id in self.data:
            vector = self.data[current_id]["vector"]
            text = self.data[current_id]["text"]
            score = self.cosine_similarity(query_vector, vector)
            scores[current_id] = {"score": score, "text": text}
        # - scores.items() get all scores items as a list of (key, value) tuples)
        # - key=lambda item: item[1]["score"] - lambda defines as item as "score"
        # from the second element of each item
        # - sorted uses as parameters: the list of tuples, the defined item and
        # reverse=True to sort in descending order
        sorted_scores = {
            k: v
            for k, v in sorted(
                scores.items(), key=lambda item: item[1]["score"], reverse=True
            )
        }
        return dict(list(sorted_scores.items())[:top_k])

    def save(self, path: str = "vectorstore.json") -> None:
        """Save the vector store JSON file to disk to be reused."""
        file_data = json.dumps(self.data, indent=4)
        fileoperations.save(file_data, path)

    def load(self, path: str = "vectorstore.json") -> None:
        """Load the vector store JSON filefrom disk."""
        self.data = fileoperations.load(path)
        if len(self.data) == 0:
            raise ValueError(
                "ERROR: VECTOR STORE FILE NOT FOUND OR EMPTY. Please run the embedder first to create the vectorstore.json file."
            )
