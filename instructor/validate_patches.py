#!/usr/bin/env python3
"""Check that each reference test catches its bug and passes after its patch."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUGS = (
    {
        "id": "BUG-01",
        "patch": "instructor/patches/bug_01.patch",
        "test": "instructor/reference-tests/test_bug_01.py",
        "exercise": "python-tests/exercises/test_bug_01.py",
        "marker": "lost update",
        "other_test": "instructor/reference-tests/test_bug_06.py",
        "other_marker": "deadlock",
    },
    {
        "id": "BUG-02",
        "patch": "instructor/patches/bug_02.patch",
        "test": "instructor/reference-tests/test_bug_02.py",
        "exercise": "python-tests/exercises/test_bug_02.py",
        "marker": "direction race",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-03",
        "patch": "instructor/patches/bug_03.patch",
        "test": "instructor/reference-tests/test_bug_03.py",
        "exercise": "python-tests/exercises/test_bug_03.py",
        "marker": "unsafe collection",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-04",
        "patch": "instructor/patches/bug_04.patch",
        "test": "instructor/reference-tests/test_bug_04.py",
        "exercise": "python-tests/exercises/test_bug_04.py",
        "marker": "visibility",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-05",
        "patch": "instructor/patches/bug_05.patch",
        "test": "instructor/reference-tests/test_bug_05.py",
        "exercise": "python-tests/exercises/test_bug_05.py",
        "marker": "check-then-act",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-06",
        "patch": "instructor/patches/bug_06.patch",
        "test": "instructor/reference-tests/test_bug_06.py",
        "exercise": "python-tests/exercises/test_bug_06.py",
        "marker": "deadlock",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-07",
        "patch": "instructor/patches/bug_07.patch",
        "test": "instructor/reference-tests/test_bug_07.py",
        "exercise": "python-tests/exercises/test_bug_07.py",
        "marker": "pause/resume race",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-08",
        "patch": "instructor/patches/bug_08.patch",
        "test": "instructor/reference-tests/test_bug_08.py",
        "exercise": "python-tests/exercises/test_bug_08.py",
        "marker": "concurrent persistence",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-09",
        "patch": "instructor/patches/bug_09.patch",
        "test": "instructor/reference-tests/test_bug_09.py",
        "exercise": "python-tests/exercises/test_bug_09.py",
        "marker": "thread leak",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
    {
        "id": "BUG-10",
        "patch": "instructor/patches/bug_10.patch",
        "test": "instructor/reference-tests/test_bug_10.py",
        "exercise": "python-tests/exercises/test_bug_10.py",
        "marker": "double collision",
        "other_test": "instructor/reference-tests/test_bug_01.py",
        "other_marker": "lost update",
    },
)


def ignore_copy(_directory, names):
    skipped = {
        ".git",
        "target",
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "venv",
    }
    return [name for name in names if name in skipped]


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def compile_java(workdir: Path) -> subprocess.CompletedProcess:
    return run(["mvn", "-B", "-DskipTests", "compile"], workdir)


def run_pytest(workdir: Path, test_path: str) -> subprocess.CompletedProcess:
    return run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", test_path],
        workdir,
    )


def combined(proc: subprocess.CompletedProcess) -> str:
    return f"{proc.stdout}\n{proc.stderr}"


def validate_one(bug: dict) -> dict:
    patch = ROOT / bug["patch"]
    if not patch.is_file():
        return {"id": bug["id"], "ok": False, "detail": f"missing patch {bug['patch']}"}

    workdir = Path(tempfile.mkdtemp(prefix=f"snake-{bug['id'].lower()}-"))
    try:
        shutil.copytree(ROOT, workdir, dirs_exist_ok=True, ignore=ignore_copy)
        compiled = compile_java(workdir)
        if compiled.returncode != 0:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": "infrastructure failure: maven compile\n" + combined(compiled),
            }

        before = run_pytest(workdir, bug["test"])
        before_text = combined(before)
        if before.returncode == 0:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": "bug was not detected; reference test passed on the defective version",
            }
        if before.returncode != 1 or bug["marker"] not in before_text:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": (
                    "infrastructure failure: expected a behavioral test failure "
                    f"containing {bug['marker']!r}, got exit {before.returncode}\n"
                    + before_text
                ),
            }

        applied = run(["git", "apply", "--check", bug["patch"]], workdir)
        if applied.returncode != 0:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": "git apply --check failed\n" + combined(applied),
            }
        applied = run(["git", "apply", bug["patch"]], workdir)
        if applied.returncode != 0:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": "git apply failed\n" + combined(applied),
            }

        rebuilt = compile_java(workdir)
        if rebuilt.returncode != 0:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": "infrastructure failure: maven compile after patch\n"
                + combined(rebuilt),
            }

        after = run_pytest(workdir, bug["test"])
        if after.returncode != 0:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": "reference test still failing after the patch\n" + combined(after),
            }

        exercise = run_pytest(workdir, bug["exercise"])
        if exercise.returncode != 0:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": "patched student test did not pass\n" + combined(exercise),
            }

        other = run_pytest(workdir, bug["other_test"])
        other_text = combined(other)
        if other.returncode == 0 or bug["other_marker"] not in other_text:
            return {
                "id": bug["id"],
                "ok": False,
                "detail": (
                    "patch changed another defect; "
                    f"{bug['other_test']} should still fail with {bug['other_marker']!r}\n"
                    + other_text
                ),
            }
        return {
            "id": bug["id"],
            "ok": True,
            "detail": (
                "detected on the defective version, passed after the patch, "
                "and left the other defect in place"
            ),
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> int:
    selected = sys.argv[1:]
    bugs = BUGS
    if selected:
        wanted = {item.upper() for item in selected}
        bugs = tuple(bug for bug in BUGS if bug["id"] in wanted)
        if not bugs:
            print("No matching bugs for", selected, file=sys.stderr)
            return 2

    results = [validate_one(bug) for bug in bugs]
    print("Patch validation report")
    print("=======================")
    failed = False
    for result in results:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"{result['id']}: {status}")
        print(result["detail"])
        print()
        failed = failed or not result["ok"]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
