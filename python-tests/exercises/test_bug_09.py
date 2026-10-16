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
    service = JClass("game.loop.GameService")()
    started = JClass("java.util.concurrent.CountDownLatch")(3)

    @jpype.JImplements("java.lang.Runnable")
    class Started:
        @jpype.JOverride
        def run(self):
            started.countDown()

    service.setBeforeTaskBody(Started())
    service.start()
    service.start()
    service.start()

    time_unit = JClass("java.util.concurrent.TimeUnit")
    if not started.await_(3, time_unit.SECONDS):
        sys.stderr.write("thread leak: tasks did not start\n")
        halt(1)

    service.stop()
    idle = bool(service.awaitIdle(1500))
    active = int(service.getActiveTasks())
    if not idle or active != 0:
        sys.stderr.write(
            f"thread leak: active tasks remained after stop active={active}\n"
        )
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
def game_service(jvm):
    return jvm.JClass("game.loop.GameService")()


@pytest.mark.timeout(30)
def test_bug_09_thread_leak(game_service, concurrency, project_dir):
    """Repeated start/stop must not leave active game tasks behind."""
    assert game_service.getActiveTasks() == 0
    completed = concurrency.run_isolated(WORKER, timeout_seconds=20, project=project_dir)
    assert completed.returncode == 0, (
        "thread leak: active tasks remained after stop\n"
        f"exit={completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )
