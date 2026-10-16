import pytest

WORKER = r"""
import os
import sys
import traceback
from pathlib import Path

root = Path(os.environ["SNAKE_PROJECT_ROOT"])
sys.path.insert(0, str(root / "python-tests"))

from helpers.jvm import ensure_jvm

jpype = ensure_jvm()
JClass = jpype.JClass


def halt(code):
    jpype.java.lang.Runtime.getRuntime().halt(code)


def main():
    session = JClass("game.engine.GameSession")()
    barrier = JClass("java.util.concurrent.CyclicBarrier")(2)
    hook = JClass("game.lab.Barriers").arrive(barrier)
    session.setAfterEngineLockAcquired(hook)
    session.setAfterScoreLockAcquired(hook)

    executors = JClass("java.util.concurrent.Executors")
    time_unit = JClass("java.util.concurrent.TimeUnit")
    timeout_type = JClass("java.util.concurrent.TimeoutException")
    executor = executors.newFixedThreadPool(2)

    @jpype.JImplements("java.util.concurrent.Callable")
    class Update:
        @jpype.JOverride
        def call(self):
            session.updateAndRecord("Ada", 10)
            return "updated"

    @jpype.JImplements("java.util.concurrent.Callable")
    class Read:
        @jpype.JOverride
        def call(self):
            return str(session.readRecordsAndState())

    futures = [executor.submit(Update()), executor.submit(Read())]
    try:
        for future in futures:
            future.get(3, time_unit.SECONDS)
    except timeout_type:
        sys.stderr.write(
            "deadlock: updateAndRecord and readRecordsAndState did not finish\n"
        )
        halt(2)

    ticks = int(session.getTicks())
    score = int(session.getScore())
    records = [str(item) for item in session.getRecords()]
    if ticks != 1 or score != 10 or records != ["Ada:10"]:
        sys.stderr.write(
            f"inconsistent state ticks={ticks} score={score} records={records}\n"
        )
        halt(1)
    sys.stdout.write("ok\n")
    halt(0)


try:
    main()
except BaseException:
    traceback.print_exc()
    halt(1)
"""


@pytest.fixture
def game_session(jvm):
    return jvm.JClass("game.engine.GameSession")()


@pytest.mark.timeout(30)
def test_bug_06_no_deadlock(game_session, concurrency, project_dir):
    """updateAndRecord and readRecordsAndState both finish, then state matches."""
    assert game_session.getTicks() == 0

    completed = concurrency.run_isolated(
        WORKER,
        timeout_seconds=20,
        project=project_dir,
    )
    assert completed.returncode == 0, (
        "deadlock: updateAndRecord and readRecordsAndState did not finish\n"
        f"exit={completed.returncode}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
