# Socratic Sprint

A Socratic code tutoring system with a multiplayer coding game.

## Stack

Frontend: React (Vite + Bun) + Tailwind + Monaco editor
Backend: Python FastAPI + WebSockets + FAISS RAG

## Setup

### Backend (uv)

```bash
uv venv
uv sync
uv run python -m backend.rag.ingest --code-kb backend/codeKnowledgebase --index-dir backend/rag/index
uv run python -m backend.problems.ingest --code-kb backend/codeKnowledgebase --output backend/problems/data/problems.jsonl
uv run uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
bun install
bun run dev
```

Open the app at `http://localhost:5173`.

## Environment

Copy `backend/.env.example` to `.env` and set keys as needed.
Copy `frontend/.env.example` to `.env` if your API base URL is different.

Key variables:

- `LLM_PROVIDER=openrouter|groq|huggingface`
- `LLM_MODEL=openrouter/free`
- `OPENROUTER_API_KEY=...`
- `HF_API_KEY=...`
- `GROQ_API_KEY=...`
- `REDIS_URL=redis://localhost:6379/0`
- `RUNNER_MODE=docker|local`
- `CONTAINER_RUNTIME=docker|podman`
- `RUNNER_FALLBACK_TO_LOCAL=true|false`
- `CODE_KB_DIR=backend/codeKnowledgebase`
- `RAG_INDEX_DIR=backend/rag/index`
- `EMBED_MODEL=intfloat/e5-base-v2`

## Notes

- `backend/.env` is loaded automatically on backend startup.
- Container sandbox is the default for Python/Java/C++ execution.
- To require containerized execution with no local fallback, set `RUNNER_MODE=docker` and `RUNNER_FALLBACK_TO_LOCAL=false`.
- To use Podman for code execution, set `CONTAINER_RUNTIME=podman`.
- The RAG index is built from `backend/codeKnowledgebase`.
- Benchmarks are offline and run from `backend/benchmarks`.

## Benchmark

```bash
uv run python -m backend.benchmarks.benchmark_cli --dataset treeinstruct --limit 50
```

Lower-cost benchmark run:

```bash
uv run python -m backend.benchmarks.benchmark_cli --dataset treeinstruct --limit 10 --candidate-count 2
```

Notes:
- Benchmarks now default to `--candidate-count 2` and heuristic verifier scoring to reduce LLM calls.
- Pass `--llm-verifier` if you want benchmark runs to use the verifier LLM as well.
