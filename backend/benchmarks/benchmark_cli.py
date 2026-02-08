from __future__ import annotations

import argparse
import json
from pathlib import Path
import asyncio

from ..config import settings
from ..deps import get_pipeline
from ..models.router import LLMRouter
from ..rag.embeddings import EmbeddingModel
from .datasets import load_treeinstruct
from .tasks import evaluate_treeinstruct


async def run(dataset: str, limit: int | None) -> dict:
    pipeline = get_pipeline()
    router = LLMRouter()
    embedder = EmbeddingModel(settings.embed_model)

    if dataset == "treeinstruct":
        items = load_treeinstruct(settings.problems_path, limit=limit)
        metrics = await evaluate_treeinstruct(pipeline, router, items, embedder)
    else:
        metrics = {}

    return {
        "dataset": dataset,
        "count": len(items) if dataset == "treeinstruct" else 0,
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["treeinstruct"], default="treeinstruct")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", type=str, default=str(Path(__file__).parent / "outputs" / "results.json"))
    args = parser.parse_args()

    result = asyncio.run(run(args.dataset, args.limit))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
