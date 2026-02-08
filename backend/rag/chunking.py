from __future__ import annotations

from typing import Iterable, List


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            if len(para) <= max_chars:
                current = para
            else:
                # hard split long paragraph
                for i in range(0, len(para), max_chars):
                    part = para[i : i + max_chars]
                    if part:
                        chunks.append(part)
                current = ""
    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        overlapped: List[str] = []
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                overlapped.append(chunk)
            else:
                prev = chunks[idx - 1]
                prefix = prev[-overlap:]
                overlapped.append(f"{prefix}\n{chunk}")
        return overlapped
    return chunks


def join_prompt_parts(parts: Iterable[str]) -> str:
    return "\n\n".join([p for p in parts if p])
