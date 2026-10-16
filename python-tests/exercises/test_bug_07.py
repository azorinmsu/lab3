import pytest

from helpers.assertions import assert_equal


def test_bug_07_pause_resume_race(concurrency, jvm):
    """Stale pause sampling must not let a tick run after pause is applied."""
    jpype = jvm
    controller = jvm.JClass("game.loop.PauseController")()
    barrier = concurrency.cyclic_barrier(2)
    pause_done = concurrency.countdown_latch(1)

    @jpype.JImplements("java.lang.Runnable")
    class PauseHook:
        @jpype.JOverride
        def run(self):
            barrier.await_()

    @jpype.JImplements("java.lang.Runnable")
    class TickHook:
        @jpype.JOverride
        def run(self):
            barrier.await_()
            pause_done.await_()

    controller.setBeforePause(PauseHook())
    controller.setBeforeTickDecision(TickHook())

    outcomes = {"ticked": None}

    def pause():
        controller.pause()
        pause_done.countDown()

    def tick():
        outcomes["ticked"] = bool(controller.tryTick())

    concurrency.invoke_all([pause, tick], timeout_seconds=5)

    assert_equal(
        outcomes["ticked"],
        False,
        "pause/resume race: tryTick ran after pause() was applied",
    )
    assert_equal(int(controller.getTicks()), 0, "pause/resume race: tick counter")
    assert controller.isPaused()
