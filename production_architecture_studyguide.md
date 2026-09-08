# Shipping AI Solutions to Production — Study Guide

Built to close the gap flagged in the Playtech technical panel: RAG fundamentals were solid, but architecture/tech stack for taking an AI solution to production wasn't. Same approach as the RAG cheat sheet — mechanism-level understanding, tied back to your own `rag-project` wherever possible, so you have a concrete example instead of only abstractions.

## 1\. The mental model: what "production" adds on top of a working pipeline

Your `rag-project` (ingest.py → query.py) is a *correct* pipeline. Production adds five concerns a prototype doesn't need: **concurrency** (many users at once, not one CLI invocation), **reliability** (the pipeline must degrade gracefully, not crash), **observability** (you must be able to tell *why* a bad answer happened, after the fact), **cost control** (every call has a dollar and latency cost that compounds at volume), and **security** (the system is now reachable by people who didn't write it).

Everything below is one of those five concerns made concrete.

## 2\. Reference architecture (a typical RAG-in-production stack)

Client → API Gateway → App/Orchestration layer → \[Vector DB, Cache, LLM API\]

                              │

                        Observability (logs/traces/metrics)

- **API Gateway**: auth, rate limiting, request validation, routing. (AWS API Gateway / Kong / a framework's own middleware — e.g. FastAPI \+ a reverse proxy.)  
- **App/orchestration layer**: your `query.py` logic, but as a long-running service (FastAPI/Flask) instead of a CLI script — handles one request at a time *concurrently*, not sequentially.  
- **Vector DB**: managed (Pinecone, Weaviate Cloud, Qdrant Cloud) or self-hosted (Qdrant/Milvus on your own infra, or FAISS embedded in the app for smaller corpora). Trade-off: managed \= no ops burden, per-query/storage cost; self-hosted \= ops burden, fixed infra cost, full control.  
- **Cache**: a semantic or exact-match cache in front of the LLM call — see §4.  
- **LLM API**: your `generation.py`'s swappable backend (Ollama/Groq/ Anthropic) is already the right shape for this — production usually keeps that abstraction so you can swap providers or add fallback providers without touching call sites.  
- **Observability**: sits alongside every layer, not just at the edges — see §5.

## 3\. Deployment: containers, orchestration, serverless

- **Containerize first, regardless of what runs it.** `Dockerfile` per service — pins the Python version, system deps (e.g. what `sentence-transformers` needs), and makes "works on my machine" a non-issue. This is the baseline, not an advanced step.  
- **Serverless (AWS Lambda, Cloud Run, Modal)**: good fit when traffic is spiky/low-volume — pay per invocation, scales to zero. Bad fit for your embedder specifically: loading `all-MiniLM-L6-v2` has real cold-start cost (model weights into memory), which serverless's on-demand start makes you pay for on *every* cold invocation unless you keep it warm.  
- **Container orchestration (Kubernetes, ECS)**: fit when you need always-on capacity, fine-grained autoscaling rules, or multiple interdependent services. Heavier to operate than serverless; the payoff is control over exactly this kind of cold-start/warm-pool tradeoff.  
- **Managed AI-app platforms (AWS Bedrock, GCP Vertex AI, Azure AI Foundry)**: bundle the vector DB, model hosting/routing, and observability into one managed surface. Faster to stand up, less portable, and you inherit whatever their embedding/vector-store choices are unless they expose swap-out points.  
- **Talking point**: "for a corpus that fits comfortably in memory, I'd containerize the FastAPI app with the embedder loaded once at startup (not per-request — that's the serverless cold-start trap) and keep it on always-on compute; I'd only reach for serverless for a genuinely spiky, low-traffic internal tool."

## 4\. Cost & latency: caching, batching, streaming

- **Prompt caching** (provider-side, e.g. Anthropic's): the model provider caches a prefix of your prompt (system instructions, few-shot examples, even retrieved context if stable) so repeated calls with the same prefix skip re-processing it — cuts both cost and latency on the input-token side. Directly applicable to your `build_prompt()` — the instruction block is identical on every call.  
- **Semantic caching**: cache *answers* keyed by embedding similarity of the question, not exact string match — "what's your refund policy" and "how do refunds work" hit the same cache entry. Trade-off: risk of serving a stale or subtly-wrong cached answer if the underlying docs changed; needs a cache-invalidation story tied to your ingest pipeline.  
- **Batching**: covered in the interview cheat sheet's N+1 story — the same principle applies to embedding *and* to any provider that supports batch inference endpoints (cheaper per-token, higher latency per batch).  
- **Streaming responses**: stream tokens back to the client as they're generated (SSE/websockets) instead of waiting for the full completion — doesn't reduce total cost or total generation time, but cuts *perceived* latency to first-token, which is usually what users actually feel.  
- **Talking point tie-back to your project**: `generation.py`'s `generate()` currently blocks until the full response returns — the production version would expose a streaming variant of that call and have the API layer forward chunks to the client as SSE.

## 5\. Observability: what to actually log for an LLM app

Standard service observability (structured logs, distributed tracing via OpenTelemetry, metrics/dashboards via Prometheus+Grafana or a vendor) applies, plus LLM-specific signals that generic APM tools don't capture by default:

- **Per-request**: which chunks were retrieved (ids \+ scores), the full assembled prompt, the raw model response, token counts in/out, latency broken down by stage (embed query → vector search → generation) so you know *which* stage is slow.  
- **Aggregate**: cost per day/user/endpoint, cache hit rate, retrieval score distribution (a sustained drop signals the corpus and the question patterns have drifted apart), faithfulness/relevancy sampled via RAGAS on a rolling basis rather than only at eval time.  
- **Why this matters for a regulated context (Playtech)**: if a player-facing agent gives a wrong answer, "what did it retrieve and what did we send the model" needs to be reconstructable after the fact — not just "the answer was wrong." This is the production analogue of the strict-grounding work you already did in `query.py`.

## 6\. Security

- **Secrets**: env vars / a secrets manager (AWS Secrets Manager, Vault) — never in source or client-side. You already fixed this once (`generation.py`'s API key) — production formalizes it with rotation and access scoping.  
- **Prompt injection**: a malicious document in the corpus, or a malicious question, can try to override your system instructions. Mitigations: keep instructions and untrusted content in clearly separated roles/tags (your XML-tag structure already helps here), never let retrieved content or user input expand the model's *tool* permissions, and treat model output as untrusted before executing anything it suggests.  
- **Rate limiting / auth**: per-user and per-IP limits at the gateway layer, both to control cost and to blunt abuse/scraping.  
- **PII handling**: if ingested docs or user queries contain PII, that needs its own retention/redaction policy — relevant at a company handling player data.

## 7\. Testing & CI/CD for an AI pipeline

- **Unit tests** for the deterministic parts — chunking, retrieval ranking logic — same as normal software (you already have `test_pipeline.py` doing this with a stub embedder).  
- **Eval suite** (RAGAS-style, from the interview cheat sheet) for the non-deterministic parts — run on every change to prompts, chunking strategy, or model version, not just once. This is the part a traditional CI pipeline doesn't have a slot for by default — it needs its own step, usually against a fixed labeled question set, with a regression threshold that fails the build.  
- **Deployment strategy**: canary or blue/green rollout for a new model version or prompt change, because "did this prompt change make answers worse" is much harder to catch pre-launch than a normal code regression — you want a fast rollback path more than you'd need for typical backend changes.

## 8\. Scaling your specific project — the concrete walkthrough

This is the answer if asked "walk me through taking *this* project to production":

1. `VectorStore`'s brute-force dict → FAISS/managed vector DB (already covered in the interview cheat sheet's "5M chunks" scaling answer).  
2. `ingest.py`/`query.py` CLI scripts → a FastAPI service; `main()`\-ified logic becomes route handlers; embedder loaded once at process startup.  
3. Add the cache layer in front of `generation.generate()`.  
4. Add structured logging around each pipeline stage (§5) and wire it to a dashboard.  
5. Put the whole app behind a gateway with auth \+ rate limiting.  
6. Containerize, deploy behind an always-on autoscaling group (not serverless, per §3's cold-start reasoning) with at least 2 replicas for availability.  
7. Add the RAGAS eval suite as a CI gate before any prompt/model change ships.

## 9\. Cloud provider AI stacks — one-line comparison

- **AWS Bedrock**: model-agnostic hosting (Anthropic, Meta, Amazon models behind one API), tight integration with the rest of AWS (IAM, Lambda, OpenSearch as a vector store).  
- **GCP Vertex AI**: Google's models (Gemini) plus a managed pipeline/eval toolchain (Vertex AI Agent Builder), integrates with BigQuery for data.  
- **Azure AI Foundry**: OpenAI models first-class, strong enterprise identity/security integration (Entra ID) — usually the default pick inside an existing Microsoft shop.  
- None of these are required knowledge depth for this role — being able to name the shape of what each offers (hosted models \+ vector store \+ observability, bundled) is enough; Playtech's JD flags Google Cloud AI / Gemini Enterprise as a bonus, not core.

## Questions worth asking them (architecture-flavored, to pair with the ones already in the interview cheat sheet)

- What does Playtech's current AI deployment stack look like — self-hosted, Bedrock/Vertex/Foundry, or a mix per business unit given the Data Mesh model?  
- For the "operational AI agents" direction — are agents currently containerized services, or running inside an existing orchestration framework?

