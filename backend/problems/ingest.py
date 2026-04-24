from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterator, List

from .schema import Problem


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _slug(path: Path) -> str:
    return path.stem.replace(" ", "-").lower()


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


def _python_to_java(python_code: str) -> str:
    """Convert Python code to Java template for display."""
    java_template = """public class Solution {
  public static void main(String[] args) {
    // Convert your Python logic here
    // Python code reference:
    // """ + python_code.replace("\n", "\n    // ") + """
  }
}
"""
    return java_template


def _python_to_cpp(python_code: str) -> str:
    """Convert Python code to C++ template for display."""
    cpp_template = """#include <iostream>
using namespace std;

int main() {
  // Convert your Python logic here
  // Python code reference:
  // """ + python_code.replace("\n", "\n  // ") + """
  
  return 0;
}
"""
    return cpp_template


def treeinstruct_problems(root: Path) -> Iterator[Problem]:
    for path in root.rglob("*.py"):
        if ".git" in path.parts:
            continue
        if "__pycache__" in path.parts:
            continue
        if path.name in {"utils.py", "extract_leetcode.py"}:
            continue
        raw = _safe_read(path)
        if not raw:
            continue
        doc, code = _extract_docstring(raw)
        if not doc:
            continue
        problem = _extract_tag(doc, "problem")
        bug_desc = _extract_tag(doc, "bug_desc")
        bug_fixes = _extract_tag(doc, "bug_fixes")
        if not problem:
            continue
        title = problem.splitlines()[0].strip() if problem else path.stem
        pid = f"treeinstruct:{_slug(path)}"
        
        # Yield Python version
        yield Problem(
            problem_id=pid,
            title=title,
            language="python",
            statement=problem,
            starter_code=code,
            buggy_code=code,
            bug_desc=bug_desc or None,
            bug_fixes=bug_fixes or None,
            topic=path.parent.name,
            source="treeinstruct",
            kind="buggy",
        )
        
        # Yield Java version (converted)
        java_code = _python_to_java(code)
        yield Problem(
            problem_id=f"{pid}:java",
            title=title,
            language="java",
            statement=problem,
            starter_code=java_code,
            buggy_code=java_code,
            bug_desc=bug_desc or None,
            bug_fixes=bug_fixes or None,
            topic=path.parent.name,
            source="treeinstruct",
            kind="buggy",
        )
        
        # Yield C++ version (converted)
        cpp_code = _python_to_cpp(code)
        yield Problem(
            problem_id=f"{pid}:cpp",
            title=title,
            language="cpp",
            statement=problem,
            starter_code=cpp_code,
            buggy_code=cpp_code,
            bug_desc=bug_desc or None,
            bug_fixes=bug_fixes or None,
            topic=path.parent.name,
            source="treeinstruct",
            kind="buggy",
        )


def striver_problems(root: Path, language: str) -> Iterator[Problem]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        if language == "python" and path.suffix.lower() != ".py":
            continue
        if language == "cpp" and path.suffix.lower() not in {".cpp", ".cc"}:
            continue
        raw = _safe_read(path)
        if not raw:
            continue
        title = path.stem.replace("_", " ")
        statement = title
        if language == "cpp":
            comment_match = re.search(r"/\*(.*?)\*/", raw, re.S)
            if comment_match:
                statement = comment_match.group(1).strip()
        pid = f"striver:{_slug(path)}"
        yield Problem(
            problem_id=pid,
            title=title,
            language=language,
            statement=statement,
            starter_code=raw,
            buggy_code=None,
            bug_desc=None,
            bug_fixes=None,
            topic=" / ".join(path.parent.parts[-2:]),
            source="striver",
            kind="solution",
        )


def build_problem_bank(code_kb_dir: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    count = 0

    tree_root = code_kb_dir / "TreeInstruct Dataset"
    if tree_root.exists():
        for prob in treeinstruct_problems(tree_root):
            _write_problem(output_path, prob)
            count += 1

    py_root = code_kb_dir / "striver-a2z-dsa-Python"
    if py_root.exists():
        for prob in striver_problems(py_root, "python"):
            _write_problem(output_path, prob)
            count += 1

    cpp_root = code_kb_dir / "Strivers-A2Z-DSA-Sheet-C++"
    if cpp_root.exists():
        for prob in striver_problems(cpp_root, "cpp"):
            _write_problem(output_path, prob)
            count += 1

    return count


def _write_problem(path: Path, prob: Problem) -> None:
    payload = {
        "id": prob.problem_id,
        "title": prob.title,
        "language": prob.language,
        "statement": prob.statement,
        "starter_code": prob.starter_code,
        "buggy_code": prob.buggy_code,
        "bug_desc": prob.bug_desc,
        "bug_fixes": prob.bug_fixes,
        "topic": prob.topic,
        "source": prob.source,
        "kind": prob.kind,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-kb", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    count = build_problem_bank(Path(args.code_kb), Path(args.output))
    print(f"Wrote {count} problems")


if __name__ == "__main__":
    main()
