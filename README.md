# Socratic Sprint

A Socratic code tutoring system with a multiplayer coding game.

## Stack

Frontend: React (Vite + Bun) + Tailwind + Monaco editor
Backend: Python FastAPI + WebSockets + prompt-driven tutoring pipeline

## Run The App

### 1. Configure the backend

```bash
cp backend/.env.example backend/.env
```

For the fastest local startup, open `backend/.env` and set:

```env
LLM_PROVIDER=mock
RUNNER_MODE=local
```

Use a real hosted model instead of `mock` only if you want live LLM responses. In that case, set `LLM_PROVIDER` to `openrouter`, `groq`, or `huggingface` and provide the matching API key.

### 2. Start the backend

```bash
uv venv
uv sync
uv run uvicorn backend.main:app --reload --port 8000
```

The backend runs at `http://localhost:8000`.

Note:
- If `backend/problems/data/problems.jsonl` does not exist yet, the backend will build it automatically on first startup.
- If you prefer to prebuild it manually, run:

```bash
uv run python -m backend.problems.ingest --code-kb backend/codeKnowledgebase --output backend/problems/data/problems.jsonl
```

### 3. Start the frontend

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

- `LLM_PROVIDER=mock|openrouter|groq|huggingface`
- `LLM_MODEL=openrouter/free`
- `OPENROUTER_API_KEY=...`
- `HF_API_KEY=...`
- `GROQ_API_KEY=...`
- `REDIS_URL=redis://localhost:6379/0`
- `RUNNER_MODE=docker|local`
- `CONTAINER_RUNTIME=docker|podman`
- `RUNNER_FALLBACK_TO_LOCAL=true|false`
- `CODE_KB_DIR=backend/codeKnowledgebase`

## Notes

- `backend/.env` is loaded automatically on backend startup.
- Container sandbox is the default for Python/Java/C++ execution.
- For the simplest local setup with no container runtime, set `RUNNER_MODE=local`.
- To require containerized execution with no local fallback, set `RUNNER_MODE=docker` and `RUNNER_FALLBACK_TO_LOCAL=false`.
- To use Podman for code execution, set `CONTAINER_RUNTIME=podman`.
- The problem bank is built from `backend/codeKnowledgebase`.
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
