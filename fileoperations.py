"""File operations for saving and loading JSON files."""

import json


def save(content: str, path: str) -> None:
    """Save the string JSON file to disk to be reused."""
    with open(path, "w") as f:
        f.write(content)


def load(path: str) -> dict:
    """Load the vectorscore JSON filefrom disk."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}
