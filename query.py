"""Defines the query called by the user."""

import logging
import os
import random
import time
import uuid
from contextlib import asynccontextmanager

import litellm
from fastapi import BackgroundTasks, FastAPI, Response, status
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import llm_factory
from ragas.metrics import Faithfulness

from embedder import Embedder
from generation import Generation
from queryLogFormatter import QueryLogFormatter
from questioncache import QuestionCache
from vectorstore import VectorStore

RAGAS_SAMPLE_RATE = 1.0
FAITHFULNESS_FLOOR = 0.75


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
    app.state.evaluator = llm_factory(
        "groq/" + os.environ.get("GROQ_MODEL"),
        provider="litellm",
        client=litellm.completion,
    )
    app.state.scorer = Faithfulness(llm=app.state.evaluator)
    yield
    app.state.questioncache.save()


app = FastAPI(lifespan=lifespan)


@app.post("/query", status_code=200)
def send_prompt(q: str, response: Response, background_tasks: BackgroundTasks) -> dict:
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

    if random.random() < RAGAS_SAMPLE_RATE:
        background_tasks.add_task(
            validate_and_cache, q, result, top_data, embedded_query
        )
    return result


async def validate_and_cache(q: str, result, top_data: dict, embedded_query):
    app.state.logger.info(
        "VALIDATING ANSWER BEFORE CACHING",
        extra={"context": {"query": q}},
    )
    context_strings = []
    for data_id in top_data:
        context_strings.append(top_data[data_id]["text"])
    sample = SingleTurnSample(
        user_input=q, response=result["answer"], retrieved_contexts=context_strings
    )
    score = await app.state.scorer.single_turn_ascore(sample)
    app.state.logger.info(
        "VALIDATION COMPLETE",
        extra={"context": {"query": q, "score": score}},
    )
    if score >= FAITHFULNESS_FLOOR:
        app.state.questioncache.add(
            q, result["answer"], embedded_query[0], list(top_data.keys())
        )  # noqa: E501
        app.state.questioncache.save()
        app.state.logger.info(
            "QUERY SAVED",
            extra={"context": {"query": q, "score": score}},
        )
