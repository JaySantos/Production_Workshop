"""Ingests documentation, chunking and creating embeddings for each chunk."""

import os
import sys

from chunking import chunk_text
from embedder import Embedder
from vectorstore import VectorStore


def main(folder=None, embedder=None, vector_store=None):
    """Take files present in folder, chunks them and embed the chunk."""
    chunks = {}
    folder = folder or sys.argv[1]
    file_list = os.listdir(folder)
    for f in file_list:
        full_path = os.path.join(folder, f)
        with open(full_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        file_content_chunks = chunk_text(file_content, 150, 5)
        for i, chunk in enumerate(file_content_chunks):
            chunks[f"{f}::{i}"] = chunk
    chunk_strings = list(chunks.values())
    e = embedder or Embedder()
    embedded_chunks = e.embed(chunk_strings)
    v = vector_store or VectorStore()
    v.add(list(chunks.keys()), embedded_chunks, chunk_strings)
    v.save()


if __name__ == "__main__":
    main()
