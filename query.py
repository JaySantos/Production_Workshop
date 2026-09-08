"""Defines the query called by the user."""

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status

from embedder import Embedder
from generation import Generation
from queryLogFormatter import QueryLogFormatter
from questioncache import QuestionCache
from vectorstore import VectorStore


def build_prompt(question: str, chunks: list[dict]) -> str:
    """Build the XML containing the instructions, question, and context."""
    prompt = "<instructions>answer the question that is inside the question tag below, using only the information provided inside the context tag. If the answer is not contained within the context, say 'I don't know'.</instructions>\n"  # noqa: E501
    if not chunks or not question:
        raise ValueError("No chunks or question provided to build the prompt.")
    prompt += "<question>" + question + "</question>\n"
    prompt += "<context>\n"
    for chunk_id in chunks:
        prompt += chunk_id + " - " + chunks[chunk_id]["text"] + "\n"
    prompt += "</context>\n"
    return prompt


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading vector store and embedder...")
    app.state.vectorstore = VectorStore()
    app.state.embedder = Embedder()
    app.state.questioncache = QuestionCache()
    app.state.vectorstore.load()
    app.state.questioncache.load()
    app.state.logger = logging.getLogger("queryLogger")
    app.state.logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    app.state.logger.addHandler(handler)
    handler.setFormatter(QueryLogFormatter())
    app.state.generation = Generation(app.state.logger)
    yield
    app.state.questioncache.save()


app = FastAPI(lifespan=lifespan)


@app.post("/query", status_code=200)
def send_prompt(q: str, response: Response) -> dict:
    result = {}
    request_id = uuid.uuid4()
    app.state.logger.info(
        "QUERY STARTED", extra={"context": {"request_id": str(request_id), "query": q}}
    )
    embed_start_time = time.perf_counter()
    embedded_query = app.state.embedder.embed([q])
    embed_time = time.perf_counter() - embed_start_time
    cached_response = app.state.questioncache.query(embedded_query[0], 0.8)
    if cached_response:
        app.state.logger.info(
            "CACHED RESPONSE FOUND",
            extra={
                "context": {
                    "request_id": str(request_id),
                    "query": q,
                    "answer": cached_response[list(cached_response.keys())[0]][
                        "response"
                    ],
                    "sources": cached_response[list(cached_response.keys())[0]]["refs"],
                }
            },
        )
        app.state.logger.info(
            "LATENCY TIMES",
            extra={
                "context": {
                    "request_id": str(request_id),
                    "embed_time": embed_time,
                }
            },
        )
        result = {
            "answer": cached_response[list(cached_response.keys())[0]]["response"],
            "sources": cached_response[list(cached_response.keys())[0]]["refs"],
        }
        return result
    query_start_time = time.perf_counter()
    top_data = app.state.vectorstore.query(embedded_query[0], 5)
    query_time = time.perf_counter() - query_start_time
    prompt = build_prompt(q, top_data)
    generate_start_time = time.perf_counter()
    result = app.state.generation.generate(prompt, request_id=str(request_id))
    generate_time = time.perf_counter() - generate_start_time
    if result is None:
        app.state.logger.error(
            "No response from LLM model.",
            extra={"context": {"request_id": str(request_id)}},
        )
        app.state.logger.info(
            "LATENCY TIMES",
            extra={
                "context": {
                    "request_id": str(request_id),
                    "embed_time": embed_time,
                    "query_time": query_time,
                    "generate_time": generate_time,
                }
            },
        )
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"answer": "Error: No response from LLM model.", "sources": []}
    sources = {}
    for data_id in top_data:
        sources[data_id] = top_data[data_id]["score"]
    app.state.logger.info(
        "SOURCES",
        extra={"context": {"request_id": str(request_id), "sources": sources}},
    )
    app.state.logger.info(
        "LATENCY TIMES",
        extra={
            "context": {
                "request_id": str(request_id),
                "embed_time": embed_time,
                "query_time": query_time,
                "generate_time": generate_time,
            }
        },
    )
    result = {"answer": result, "sources": list(top_data.keys())}
    app.state.questioncache.add(
        q, result["answer"], embedded_query[0], list(top_data.keys())
    )  # noqa: E501
    app.state.questioncache.save()
    return result

    # print(result)
    # print()
    # print("Source Chunks:")
    # for data_id in top_data:
    #     print(data_id)


# def main(query_text=None, vector_store=None, embedder=None, generation=None):
#     """Run the query from argument 1 using the documents embedded and stored in disk."""
#     v = vector_store or VectorStore()
#     e = embedder or Embedder()
#     v.load()
#     app = FastAPI()

#     @app.post("/query/{query}")
#     def send_prompt(query: str):
#         g = generation or Generation()
#         embedded_query = e.embed([query])
#         top_data = v.query(embedded_query[0], 5)
#         prompt = build_prompt(query, top_data)
#         result = g.generate(prompt)
#         print(result)
#         print()
#         print("Source Chunks:")
#         for data_id in top_data:
#             print(data_id)


# if __name__ == "__main__":
#     main()
