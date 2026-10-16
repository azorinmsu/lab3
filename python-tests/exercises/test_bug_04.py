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
    loop = JClass("game.loop.GameLoop")()
    latch = JClass("java.util.concurrent.CountDownLatch")(1)
    time_unit = JClass("java.util.concurrent.TimeUnit")

    @jpype.JImplements("java.lang.Runnable")
    class AfterTick:
        @jpype.JOverride
        def run(self):
            latch.countDown()

    loop.setAfterTick(AfterTick())
    loop.startFlag()

    @jpype.JImplements("java.lang.Runnable")
    class Body:
        @jpype.JOverride
        def run(self):
            loop.run()

    thread = JClass("java.lang.Thread")(Body())
    thread.start()
    if not latch.await_(3, time_unit.SECONDS):
        sys.stderr.write("visibility: loop did not tick\n")
        halt(1)
    loop.stop()
    thread.join(2000)
    if thread.isAlive():
        sys.stderr.write("visibility: stop() was not observed by the game loop\n")
        halt(2)
    sys.stdout.write("ok\n")
    halt(0)


try:
    main()
except BaseException:
    traceback.print_exc()
    halt(1)
"""


@pytest.fixture
def game_loop(jvm):
    return jvm.JClass("game.loop.GameLoop")()


@pytest.mark.timeout(30)
def test_bug_04_visibility(game_loop, concurrency, project_dir):
    """stop() must be visible to the loop so run() exits promptly."""
    assert game_loop.getTicks() == 0
    completed = concurrency.run_isolated(WORKER, timeout_seconds=15, project=project_dir)
    assert completed.returncode == 0, (
        "visibility: stop() was not observed by the game loop\n"
        f"exit={completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )
