"""Create the JSON file containing the embedding of the documentation chunks."""

import datetime
import json

import fileoperations
from vectorstore import VectorStore


class QuestionCache:
    """Create the JSON file containing the embedding of the questions cached."""

    def __init__(self):
        """Init function."""
        self.data = {}

    def add(
        self, question: str, response: str, vector: list[float], refs: list[str]
    ) -> None:  # noqa: E501
        """Add the IDs, arrays of vectors, and raw texts to the data dictionary."""
        question_id = 0 if len(self.data) == 0 else max(self.data) + 1  # noqa: E501
        self.data[question_id] = {  # noqa: E501
            "question": question,
            "response": response,
            "vector": vector,
            "refs": refs,
            "time": datetime.datetime.now().isoformat(),
        }  # noqa: E501

    def query(self, query_vector: list[float], threshold: float) -> dict:
        """Run cosine_similarity between the query_vector and all vectors in self.data.

        Returns the top self.data entry by cosine_similarity if that entry score is above the threshold, otherwise returns an empty dict.
        """
        cached_question = {}
        stored_id = None
        for current_id in self.data:
            vector = self.data[current_id]["vector"]
            question = self.data[current_id]["question"]
            score = VectorStore.cosine_similarity(query_vector, vector)
            if score >= threshold and (
                (len(cached_question) == 0)
                or (score > cached_question[stored_id]["score"])
            ):  # noqa: E501
                stored_id = current_id
                cached_question.clear()
                cached_question[current_id] = {
                    "score": score,
                    "question": question,
                    "response": self.data[current_id]["response"],
                    "refs": self.data[current_id]["refs"],
                }
        return cached_question

    def save(self, path: str = "questioncache.json") -> None:
        """Save the question cache JSON file to disk to be reused."""
        file_data = json.dumps(self.data, indent=4)
        fileoperations.save(file_data, path)

    def load(self, path: str = "questioncache.json") -> None:
        """Load the question cache JSON filefrom disk."""
        self.data = fileoperations.load(path)
