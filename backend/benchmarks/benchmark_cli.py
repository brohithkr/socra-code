from __future__ import annotations

import argparse
import json
from pathlib import Path
import asyncio

from ..deps import get_pipeline
from ..models.router import LLMRouter
from .embeddings import EmbeddingModel
from .datasets import load_treeinstruct
from .tasks import evaluate_treeinstruct


async def run(
    dataset: str,
    limit: int | None,
    candidate_count: int,
    verifier_use_llm: bool,
) -> dict:
    pipeline = get_pipeline()
    router = LLMRouter()
    embedder = EmbeddingModel()

    if dataset == "treeinstruct":
        items = load_treeinstruct(settings.problems_path, limit=limit)
        metrics = await evaluate_treeinstruct(
            pipeline,
            router,
            items,
            embedder,
            candidate_count=candidate_count,
            verifier_use_llm=verifier_use_llm,
        )
    else:
        metrics = {}

    return {
        "dataset": dataset,
        "count": len(items) if dataset == "treeinstruct" else 0,
        "candidate_count": candidate_count,
        "verifier_use_llm": verifier_use_llm,
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["treeinstruct"], default="treeinstruct")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--candidate-count", type=int, default=2)
    parser.add_argument("--llm-verifier", action="store_true")
    parser.add_argument("--output", type=str, default=str(Path(__file__).parent / "outputs" / "results.json"))
    args = parser.parse_args()

    result = asyncio.run(run(args.dataset, args.limit, args.candidate_count, args.llm_verifier))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
