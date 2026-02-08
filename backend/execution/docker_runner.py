from __future__ import annotations

import asyncio
import shutil
import tempfile
import time
from typing import Tuple

from ..config import settings


async def run_in_docker(language: str, code: str, stdin: str | None = None) -> Tuple[bool, str, str, int, int]:
    if not shutil.which("docker"):
        return False, "", "docker not available", 127, 0

    image_map = {
        "python": "python:3.11-slim",
        "java": "openjdk:17-slim",
        "cpp": "gcc:13",
        "c++": "gcc:13",
    }
    image = image_map.get(language)
    if not image:
        return False, "", f"Unsupported language: {language}", 1, 0

    start = time.time()
    with tempfile.TemporaryDirectory() as tmpdir:
        if language == "python":
            file_name = "main.py"
        elif language == "java":
            file_name = "Main.java"
        else:
            file_name = "main.cpp"
        file_path = f"{tmpdir}/{file_name}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        if language == "python":
            cmd = ["python", f"/work/{file_name}"]
        elif language == "java":
            cmd = ["bash", "-lc", "javac /work/Main.java && java -cp /work Main"]
        else:
            cmd = ["bash", "-lc", "g++ /work/main.cpp -O2 -std=c++17 -o /work/a.out && /work/a.out"]

        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{tmpdir}:/work",
            image,
            *cmd,
        ]

        proc = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdin=asyncio.subprocess.PIPE if stdin else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin.encode() if stdin else None),
                timeout=settings.max_run_seconds,
            )
        except asyncio.TimeoutError:
            proc.kill()
            return False, "", "Execution timed out", 124, int((time.time() - start) * 1000)

    duration_ms = int((time.time() - start) * 1000)
    return proc.returncode == 0, stdout.decode(), stderr.decode(), proc.returncode, duration_ms
