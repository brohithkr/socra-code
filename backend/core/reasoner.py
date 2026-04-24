from __future__ import annotations

from ..models.router import LLMRouter


class Reasoner:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def summarize(self, code: str, output: str | None) -> str:
        prompt = self._build_prompt(code, output)
        system = "You are a code reasoning assistant. Return a concise bug diagnosis summary." 
        outputs = await self.router.complete(role="reasoner", system=system, prompt=prompt, n=1, temperature=0.3)
        return outputs[0]

    def _build_prompt(self, code: str, output: str | None) -> str:
        output_block = output or "(no runtime output)"
        return (
            "Analyze the buggy code and output.\n"
            f"Output: {output_block}\n"
            "Code:\n"
            f"{code}\n"
            "Return a short diagnosis (2-4 sentences)."
        )
