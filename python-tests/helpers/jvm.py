"""Start one JPype JVM per process against the Maven build output."""

from __future__ import annotations

import os
from pathlib import Path

import jpype

_jvm_requested = False


def project_root() -> Path:
    override = os.environ.get("SNAKE_PROJECT_ROOT")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[2]


def classes_directory(root: Path | None = None) -> Path:
    root = root or project_root()
    classes = root / "target" / "classes"
    if not classes.is_dir():
        raise RuntimeError(
            "Maven build artifacts were not found at "
            f"{classes}. Compile the project first:\n"
            "  mvn -B -DskipTests compile"
        )
    if not any(classes.rglob("*.class")):
        raise RuntimeError(
            f"{classes} exists but contains no .class files. "
            "Run: mvn -B -DskipTests compile"
        )
    return classes


def ensure_jvm():
    """Start the JVM once. Refuses to start it again after shutdown."""
    global _jvm_requested

    if jpype.isJVMStarted():
        return jpype

    if _jvm_requested:
        raise RuntimeError(
            "The JVM was already started and shut down in this process. "
            "JPype cannot restart it. Run the test in a new Python process."
        )

    classes = classes_directory()
    _jvm_requested = True
    try:
        jpype.startJVM(classpath=[str(classes)], convertStrings=True)
    except OSError as exc:
        message = str(exc).lower()
        if "restart" in message or "already" in message:
            raise RuntimeError(
                "The JVM was already started and shut down in this process. "
                "JPype cannot restart it. Run the test in a new Python process."
            ) from exc
        raise RuntimeError(
            "Failed to start the JVM for the Snake project. "
            f"Classpath: {classes}. Original error: {exc}"
        ) from exc
    return jpype
