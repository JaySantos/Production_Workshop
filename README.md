# Production RAG Service with Grafana Observability

A retrieval-augmented generation (RAG) service built to explore what it takes to move an LLM prototype into production: a long-running API, a semantic answer cache with an automated quality gate, and structured logs that flow into Grafana through Loki and Promtail.

The service answers questions about a small set of sample company docs (product FAQ, billing, refunds, security) and only uses the retrieved context to answer.

## What it does

- **FastAPI query service** (`query.py`): embeds the question, retrieves the top 5 chunks, builds a grounded prompt and calls the LLM.
- **Semantic question cache** (`questioncache.py`): similar questions (cosine similarity ≥ 0.8) are answered from the cache, skipping retrieval and generation.
- **Quality gate before caching**: each new answer is scored for faithfulness with [Ragas](https://docs.ragas.io/) in a background task. Only answers scoring ≥ 0.75 are cached, so bad answers aren't served again.
- **Swappable LLM backend** (`generation.py`): any OpenAI-compatible chat completions endpoint, configured for Groq or NVIDIA via environment variables.
- **Structured JSON logging** (`queryLogFormatter.py`): every log line carries a `request_id`, plus stage timings, token usage, retrieved sources, cache hits and errors.
- **Observability stack** (`docker-compose.yml`, `observability/`): Promtail collects container logs and ships them to Loki. Grafana starts with the Loki data source and a ready-made **RAG Service Overview** dashboard already provisioned.

## Architecture

```
                 ┌──────────────────────── query-service (FastAPI) ────────────────────────┐
POST /query ───► │ embed (all-MiniLM-L6-v2) ─► question cache hit? ──yes──► cached answer   │
                 │                                   │ no                                    │
                 │                                   ▼                                       │
                 │        vector store (top 5) ─► prompt ─► LLM (Groq / NVIDIA) ─► answer    │
                 │                                                    │                      │
                 │                         background: Ragas faithfulness ≥ 0.75 ─► cache    │
                 └───────────────────────────────────┬─────────────────────────────────────┘
                                                     │ JSON logs (stdout)
                                                     ▼
                               Promtail ─────► Loki ─────► Grafana
```

## Project layout

| Path | Purpose |
|---|---|
| `ingest.py` | Chunks every file in a folder, embeds the chunks and writes `vectorstore.json` |
| `chunking.py` | Fixed-size chunking with overlap |
| `embedder.py` | Sentence Transformers embeddings (`all-MiniLM-L6-v2`, normalised) |
| `vectorstore.py` | Minimal JSON-backed vector store with cosine similarity search |
| `query.py` | FastAPI app: `/query` endpoint, caching, Ragas validation, logging |
| `generation.py` | LLM client for OpenAI-compatible endpoints |
| `questioncache.py` | Semantic cache of validated answers |
| `queryLogFormatter.py` | JSON log formatter that merges per-request context |
| `observability/` | Loki and Promtail configuration |
| `observability/grafana/` | Grafana provisioning (Loki data source) and the RAG Service Overview dashboard |
| `docs/` | Sample documents used as the knowledge base |
| `tests/` | pytest suite for ingestion, chunking, embeddings, vector store, prompt building, generation and the query endpoint |
| `production_architecture_studyguide.md` | Notes on production concerns: deployment, caching, observability, security, testing |

## Getting started

### Prerequisites

- Docker and Docker Compose
- An API key for [Groq](https://console.groq.com/) (also used by Ragas for evaluation) and, optionally, NVIDIA

### 1. Configure environment

Create a `.env` file in the project root (it's git-ignored):

```env
GENERATION_BACKEND=groq          # or: nvidia

GROQ_API_KEY=your-groq-key
GROQ_URL=https://api.groq.com/openai/v1
GROQ_MODEL=your-groq-model-id

# Only needed when GENERATION_BACKEND=nvidia
NVIDIA_API_KEY=your-nvidia-key
NVIDIA_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=your-nvidia-model-id
```

`GROQ_MODEL` is always required, because Ragas uses Groq through LiteLLM to score answers.

### 2. Start the stack

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Query API (with Swagger UI at `/docs`) | http://localhost:8000 |
| Grafana (opens on the RAG Service Overview dashboard) | http://localhost:3000 |
| Loki | http://localhost:3100 |

### 3. Ask a question

```bash
curl -X POST "http://localhost:8000/query?q=How%20do%20I%20request%20a%20refund%3F"
```

Response:

```json
{
  "answer": "...",
  "sources": ["sample_refund_policy.md::0", "..."]
}
```

Ask the same question again, or a close rewording, and once the answer has passed validation it comes back from the cache.

## Exploring the logs in Grafana

Grafana runs with anonymous admin access, for local use only. Nothing needs setting up: the Loki data source and dashboard are provisioned from `observability/grafana/` when the container starts.

### RAG Service Overview dashboard

Open http://localhost:3000 and send a few queries. The dashboard refreshes every 10 seconds and shows:

| Panel | What it tells you |
|---|---|
| Queries, Cache hits, Answers cached, Errors | Totals for the selected time range |
| Latency by stage | Average seconds for embedding, retrieval and the LLM call |
| Faithfulness score (Ragas) | Quality score of new answers. 0.75 or above gets cached |
| Token usage | Prompt and completion tokens sent to the LLM |
| Cache hits vs LLM calls | How much traffic the cache is absorbing |
| Service logs | Live log stream. Paste a `request_id` into the box at the top to follow one request end to end |

### Ad hoc queries in Explore

Go to **Explore**, pick Loki, and try these queries.

All logs from the query service, parsed as JSON:

```logql
{container=~".+query-service.+"} | json
```

Trace a single request end to end:

```logql
{container=~".+query-service.+"} | json | request_id="<paste-a-request-id>"
```

Cache hits only:

```logql
{container=~".+query-service.+"} | json | message="CACHED RESPONSE FOUND"
```

Errors (LLM timeouts, bad responses):

```logql
{container=~".+query-service.+"} | json | levelname="ERROR"
```

Average LLM generation time over 5 minutes:

```logql
avg_over_time({container=~".+query-service.+"} | json | message="LATENCY TIMES" | generate_time != "" | unwrap generate_time [5m])
```

Faithfulness scores from the quality gate:

```logql
{container=~".+query-service.+"} | json | message="VALIDATION COMPLETE" | line_format "{{.score}}  {{.query}}"
```

### What gets logged

| Message | Key fields |
|---|---|
| `QUERY STARTED` | `request_id`, `query` |
| `CACHED RESPONSE FOUND` | `request_id`, `answer`, `sources` |
| `QUERY SENT TO MODEL` | `request_id`, `prompt` |
| `TOKEN USAGE:` | `prompt_tokens`, `completion_tokens`, `total_tokens` |
| `SOURCES` | `request_id`, retrieved chunk IDs with similarity scores |
| `LATENCY TIMES` | `embed_time`, `query_time`, `generate_time` (seconds) |
| `VALIDATION COMPLETE` | `query`, faithfulness `score` |
| `QUERY SAVED` | `query`, `score` |

## Running locally without Docker

```bash
uv sync                      # or: pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)
fastapi dev query.py
```

## Rebuilding the knowledge base

Put your own Markdown or text files in a folder and run:

```bash
python ingest.py docs
```

This rewrites `vectorstore.json`. Rebuild the container afterwards (`docker compose up --build`) because the file is copied into the image.

## Tests and linting

```bash
pytest
ruff check .
```

## Known limitations

- The vector store and question cache are JSON files, which is fine for a small corpus but not for concurrent writes or large datasets.
- The question cache lives inside the container and isn't mounted as a volume, so it resets when the container is recreated.
- Logs only so far. There are no metrics (Prometheus) or traces (Tempo / OpenTelemetry) yet.
