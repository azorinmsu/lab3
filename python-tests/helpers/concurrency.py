"""Concurrency helpers backed by java.util.concurrent, not Thread.sleep."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import jpype

from helpers.jvm import ensure_jvm, project_root

_PROXIES = {}


def _ensure_proxies():
    ensure_jvm()
    if _PROXIES.get("ready"):
        return _PROXIES

    @jpype.JImplements("java.lang.Runnable")
    class PyRunnable:
        def __init__(self, fn):
            self._fn = fn

        @jpype.JOverride
        def run(self):
            self._fn()

    @jpype.JImplements("java.util.concurrent.Callable")
    class PyCallable:
        def __init__(self, fn):
            self._fn = fn

        @jpype.JOverride
        def call(self):
            return self._fn()

    _PROXIES["runnable"] = PyRunnable
    _PROXIES["callable"] = PyCallable
    _PROXIES["ready"] = True
    return _PROXIES


def countdown_latch(count: int):
    ensure_jvm()
    return jpype.JClass("java.util.concurrent.CountDownLatch")(count)


def cyclic_barrier(parties: int):
    ensure_jvm()
    return jpype.JClass("java.util.concurrent.CyclicBarrier")(parties)


def await_barrier(barrier):
    """Call CyclicBarrier.await. JPype exposes it as ``await_``."""
    barrier.await_()


def await_latch(latch, timeout_seconds: float | None = None) -> bool:
    """Call CountDownLatch.await. JPype exposes it as ``await_``."""
    ensure_jvm()
    if timeout_seconds is None:
        latch.await_()
        return True
    time_unit = jpype.JClass("java.util.concurrent.TimeUnit")
    millis = max(1, int(timeout_seconds * 1000))
    return bool(latch.await_(millis, time_unit.MILLISECONDS))


def java_runnable(fn):
    """Adapt a Python callable to java.lang.Runnable."""
    return _ensure_proxies()["runnable"](fn)


def java_callable(fn):
    """Adapt a Python callable to java.util.concurrent.Callable."""
    return _ensure_proxies()["callable"](fn)


def await_futures(futures, timeout_seconds: float):
    """Wait for Java futures until a shared deadline. Raises TimeoutError."""
    ensure_jvm()
    time_unit = jpype.JClass("java.util.concurrent.TimeUnit")
    timeout_type = jpype.JClass("java.util.concurrent.TimeoutException")
    deadline = time.monotonic() + timeout_seconds
    results = []
    for future in futures:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(
                "timed out waiting for futures\n" + thread_diagnostics()
            )
        millis = max(1, int(remaining * 1000))
        try:
            results.append(future.get(millis, time_unit.MILLISECONDS))
        except timeout_type as exc:
            raise TimeoutError(
                "timed out waiting for futures\n" + thread_diagnostics()
            ) from exc
    return results


def invoke_all(functions, timeout_seconds: float = 10):
    """Run callables on a fixed pool and wait until they finish or time out."""
    ensure_jvm()
    if not functions:
        return []
    executors = jpype.JClass("java.util.concurrent.Executors")
    executor = executors.newFixedThreadPool(len(functions))
    futures = [executor.submit(java_callable(fn)) for fn in functions]
    try:
        return await_futures(futures, timeout_seconds)
    finally:
        if not shutdown_executor(executor, timeout_seconds):
            executor.shutdownNow()


def run_together(functions, timeout_seconds: float = 10):
    """Start every callable at the same CyclicBarrier, then wait for all."""
    ensure_jvm()
    parties = len(functions)
    if parties == 0:
        return []
    barrier = cyclic_barrier(parties)

    def wrap(fn):
        def task():
            await_barrier(barrier)
            return fn()

        return task

    return invoke_all([wrap(fn) for fn in functions], timeout_seconds)


def shutdown_executor(executor, timeout_seconds: float = 5) -> bool:
    """Shut an ExecutorService down and report whether it terminated in time."""
    ensure_jvm()
    time_unit = jpype.JClass("java.util.concurrent.TimeUnit")
    executor.shutdown()
    return bool(executor.awaitTermination(int(timeout_seconds), time_unit.SECONDS))


def thread_diagnostics() -> str:
    """Summarise live Java threads for failure messages."""
    ensure_jvm()
    thread_cls = jpype.JClass("java.lang.Thread")
    traces = thread_cls.getAllStackTraces()
    lines = []
    for entry in traces.entrySet():
        thread = entry.getKey()
        lines.append(f"{thread.getName()} state={thread.getState()}")
    lines.sort()
    return "\n".join(lines)


def run_isolated(script: str, timeout_seconds: float, project: Path | None = None):
    """
    Run a Python script in a child process with its own JVM.

    The child is killed when ``timeout_seconds`` elapses, so a deadlocked
    Java thread cannot block the pytest process.
    """
    root = (project or project_root()).resolve()
    env = os.environ.copy()
    env["SNAKE_PROJECT_ROOT"] = str(root)
    python_tests = str(root / "python-tests")
    env["PYTHONPATH"] = python_tests + os.pathsep + env.get("PYTHONPATH", "")
    try:
        return subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            start_new_session=True,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stderr += "\ndeadlock: isolated process timed out and was killed\n"
        return subprocess.CompletedProcess(
            args=exc.cmd,
            returncode=124,
            stdout=stdout,
            stderr=stderr,
        )
