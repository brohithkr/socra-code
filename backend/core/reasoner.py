from __future__ import annotations

from ..models.router import LLMRouter


class Reasoner:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def summarize(self, code: str, error: str | None, rag_snippets: list[str]) -> str:
        prompt = self._build_prompt(code, error, rag_snippets)
        system = "You are a code reasoning assistant. Return a concise bug diagnosis summary." 
        outputs = await self.router.complete(role="reasoner", system=system, prompt=prompt, n=1, temperature=0.3)
        return outputs[0]

    def _build_prompt(self, code: str, error: str | None, rag_snippets: list[str]) -> str:
        error_block = error or "(no runtime error)"
        rag_block = "\n\n".join(rag_snippets) if rag_snippets else "(none)"
        return (
            "Analyze the buggy code and error. Use RAG snippets only as context.\n"
            f"Error: {error_block}\n"
            "Code:\n"
            f"{code}\n"
            "RAG snippets:\n"
            f"{rag_block}\n"
            "Return a short diagnosis (2-4 sentences)."
        )
