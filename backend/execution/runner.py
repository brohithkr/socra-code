from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
import time
from typing import Tuple

from ..config import settings


async def run_code(language: str, code: str, stdin: str | None = None) -> Tuple[bool, str, str, int, int]:
    if settings.runner_mode == "docker":
        from .docker_runner import run_in_container

        ok, stdout, stderr, exit_code, duration_ms = await run_in_container(language, code, stdin)
        container_unavailable = exit_code == 127 and "not available" in stderr.lower()
        if not container_unavailable:
            return ok, stdout, stderr, exit_code, duration_ms
        if not settings.runner_fallback_to_local:
            return ok, stdout, stderr, exit_code, duration_ms
        # fallback to local only when explicitly allowed
    return await _run_local(language, code, stdin)


async def _run_local(language: str, code: str, stdin: str | None) -> Tuple[bool, str, str, int, int]:
    start = time.time()
    stdout = ""
    stderr = ""
    exit_code = 1
    ok = False

    with tempfile.TemporaryDirectory() as tmpdir:
        if language == "python":
            file_path = os.path.join(tmpdir, "main.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = ["python3", file_path]
        elif language == "java":
            if not shutil.which("javac"):
                return False, "", "javac not available", 127, 0
            file_path = os.path.join(tmpdir, "Main.java")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            compile_cmd = ["javac", file_path]
            compile_proc = await _run_process(compile_cmd, cwd=tmpdir, timeout=settings.max_run_seconds)
            if compile_proc[2] != 0:
                duration_ms = int((time.time() - start) * 1000)
                return False, compile_proc[0], compile_proc[1], compile_proc[2], duration_ms
            cmd = ["java", "Main"]
        elif language in {"cpp", "c++"}:
            if not shutil.which("g++"):
                return False, "", "g++ not available", 127, 0
            file_path = os.path.join(tmpdir, "main.cpp")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            bin_path = os.path.join(tmpdir, "a.out")
            compile_cmd = ["g++", file_path, "-O2", "-std=c++17", "-o", bin_path]
            compile_proc = await _run_process(compile_cmd, cwd=tmpdir, timeout=settings.max_run_seconds)
            if compile_proc[2] != 0:
                duration_ms = int((time.time() - start) * 1000)
                return False, compile_proc[0], compile_proc[1], compile_proc[2], duration_ms
            cmd = [bin_path]
        else:
            return False, "", f"Unsupported language: {language}", 1, 0

        proc_stdout, proc_stderr, exit_code = await _run_process(
            cmd,
            cwd=tmpdir,
            timeout=settings.max_run_seconds,
            stdin=stdin,
        )
        stdout = proc_stdout
        stderr = proc_stderr
        ok = exit_code == 0

    duration_ms = int((time.time() - start) * 1000)
    return ok, stdout, stderr, exit_code, duration_ms


async def _run_process(cmd, cwd: str, timeout: float, stdin: str | None = None):
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdin=asyncio.subprocess.PIPE if stdin else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=stdin.encode() if stdin else None),
            timeout=timeout,
        )
        return stdout.decode(), stderr.decode(), proc.returncode
    except asyncio.TimeoutError:
        return "", "Execution timed out", 124
