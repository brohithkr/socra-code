# Benchmarks

This folder is for offline benchmarking only. It is not used at runtime.

## Run the benchmark

```bash
uv run python -m backend.benchmarks.benchmark_cli --dataset treeinstruct --limit 50
```

The results are written to:

```
backend/benchmarks/outputs/results.json
```

## Metrics

The CLI computes MathTutorBench-style metrics from real TreeInstruct problems:

- Problem solving (alignment to bug description)
- Socratic questioning
- Student solution correctness (LLM classification)
- Mistake location
- Mistake correction
- Scaffolding generation (verifier score)
- Pedagogy following
