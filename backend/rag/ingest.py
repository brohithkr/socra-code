from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

import faiss
from tqdm import tqdm

from .schema import Document
from .chunking import chunk_text
from .embeddings import EmbeddingModel


TREEINSTRUCT_TAGS = ("problem", "bug_desc", "bug_fixes")


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _slug_from_path(path: Path) -> str:
    return path.stem.replace(" ", "-").lower()


def _lang_from_ext(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".py":
        return "python"
    if ext in {".cpp", ".cc", ".cxx"}:
        return "cpp"
    if ext == ".js":
        return "javascript"
    return "text"


def _extract_docstring(text: str) -> tuple[str, str]:
    match = re.search(r"\"\"\"(.*?)\"\"\"", text, re.S)
    if not match:
        match = re.search(r"'''(.*?)'''", text, re.S)
    if not match:
        return "", text
    return match.group(1), text[match.end() :].strip()


def _extract_tag(doc: str, tag: str) -> str:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", doc, re.S | re.I)
    return match.group(1).strip() if match else ""


def _treeinstruct_documents(root: Path) -> Iterator[Document]:
    for path in root.rglob("*.py"):
        if ".git" in path.parts:
            continue
        if "__pycache__" in path.parts:
            continue
        if path.name == "utils.py" or path.name.startswith("extract_"):
            continue
        raw = _safe_read(path)
        if not raw:
            continue
        docstring, code = _extract_docstring(raw)
        if not docstring:
            continue
        problem = _extract_tag(docstring, "problem")
        bug_desc = _extract_tag(docstring, "bug_desc")
        bug_fixes = _extract_tag(docstring, "bug_fixes")
        if not (problem or bug_desc or bug_fixes):
            continue
        slug = _slug_from_path(path)
        text = "\n\n".join(
            part for part in [problem, bug_desc, bug_fixes, code] if part
        )
        for idx, chunk in enumerate(chunk_text(text)):
            doc_id = f"treeinstruct:{slug}:{idx}"
            yield Document(
                doc_id=doc_id,
                text=chunk,
                metadata={
                    "source": "treeinstruct",
                    "path": str(path),
                    "problem_slug": slug,
                    "language": "python",
                    "kind": "buggy",
                },
            )


def _striver_documents(root: Path) -> Iterator[Document]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".py", ".cpp", ".cc"}:
            continue
        raw = _safe_read(path)
        if not raw:
            continue
        lang = _lang_from_ext(path)
        topic = " / ".join(path.parent.parts[-2:])
        slug = _slug_from_path(path)
        text = raw
        if path.suffix.lower() in {".cpp", ".cc"}:
            comment_match = re.search(r"/\*(.*?)\*/", raw, re.S)
            if comment_match:
                header = comment_match.group(1).strip()
                text = f"{header}\n\n{raw}"
        for idx, chunk in enumerate(chunk_text(text)):
            doc_id = f"striver:{slug}:{idx}"
            yield Document(
                doc_id=doc_id,
                text=chunk,
                metadata={
                    "source": "striver",
                    "path": str(path),
                    "problem_slug": slug,
                    "language": lang,
                    "topic": topic,
                    "kind": "solution",
                },
            )


def _js_algo_documents(root: Path) -> Iterator[Document]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        if "__tests__" in path.parts or "__test__" in path.parts:
            continue
        if path.suffix.lower() not in {".js", ".md"}:
            continue
        if path.suffix.lower() == ".md" and path.name != "README.md":
            continue
        raw = _safe_read(path)
        if not raw:
            continue
        slug = _slug_from_path(path)
        topic = " / ".join(path.parent.parts[-3:])
        for idx, chunk in enumerate(chunk_text(raw)):
            doc_id = f"jsalgo:{slug}:{idx}"
            yield Document(
                doc_id=doc_id,
                text=chunk,
                metadata={
                    "source": "javascript-algorithms",
                    "path": str(path),
                    "problem_slug": slug,
                    "language": "javascript",
                    "topic": topic,
                    "kind": "reference",
                },
            )


def iter_documents(code_kb_dir: Path) -> Iterator[Document]:
    treeinstruct = code_kb_dir / "TreeInstruct Dataset"
    if treeinstruct.exists():
        yield from _treeinstruct_documents(treeinstruct)

    striver_py = code_kb_dir / "striver-a2z-dsa-Python"
    if striver_py.exists():
        yield from _striver_documents(striver_py)

    striver_cpp = code_kb_dir / "Strivers-A2Z-DSA-Sheet-C++"
    if striver_cpp.exists():
        yield from _striver_documents(striver_cpp)

    js_algo = code_kb_dir / "javascript-algorithms" / "src"
    if js_algo.exists():
        yield from _js_algo_documents(js_algo)


def build_index(
    code_kb_dir: Path,
    index_dir: Path,
    embed_model: str,
    batch_size: int = 32,
    limit: Optional[int] = None,
) -> dict:
    index_dir.mkdir(parents=True, exist_ok=True)
    docs_path = index_dir / "docs.jsonl"
    meta_path = index_dir / "index_meta.json"
    index_path = index_dir / "faiss.index"

    if docs_path.exists():
        docs_path.unlink()
    if index_path.exists():
        index_path.unlink()

    embedder = EmbeddingModel(embed_model)
    index = faiss.IndexFlatIP(embedder.dimension)

    buffer_texts: List[str] = []
    buffer_docs: List[Document] = []
    count = 0

    def flush():
        nonlocal count
        if not buffer_texts:
            return
        vectors = embedder.encode(buffer_texts, batch_size=batch_size)
        index.add(vectors)
        with docs_path.open("a", encoding="utf-8") as f:
            for doc in buffer_docs:
                payload = {
                    "doc_id": doc.doc_id,
                    "text": doc.text,
                    "metadata": doc.metadata,
                }
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
                count += 1
        buffer_texts.clear()
        buffer_docs.clear()

    for doc in tqdm(iter_documents(code_kb_dir), desc="Indexing"):
        buffer_texts.append(doc.text)
        buffer_docs.append(doc)
        if limit and count + len(buffer_texts) >= limit:
            flush()
            break
        if len(buffer_texts) >= batch_size:
            flush()

    flush()
    faiss.write_index(index, str(index_path))
    meta = {
        "created_at": time.time(),
        "count": count,
        "embed_model": embed_model,
        "code_kb_dir": str(code_kb_dir),
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-kb", type=str, required=True)
    parser.add_argument("--index-dir", type=str, required=True)
    parser.add_argument("--embed-model", type=str, default="intfloat/e5-base-v2")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    meta = build_index(
        code_kb_dir=Path(args.code_kb),
        index_dir=Path(args.index_dir),
        embed_model=args.embed_model,
        limit=args.limit,
    )
    print(f"Indexed {meta['count']} documents")


if __name__ == "__main__":
    main()
