import pytest

from helpers.assertions import assert_true


def test_bug_02_direction_race(concurrency, jvm):
    """Concurrent commands must not apply a 180-degree reverse within one tick."""
    Direction = jvm.JClass("game.control.Direction")
    controller = jvm.JClass("game.control.DirectionController")()
    controller.beginTick()
    up_done = concurrency.countdown_latch(1)

    def go_up():
        controller.setDirection(Direction.UP)
        up_done.countDown()

    def go_left():
        concurrency.await_latch(up_done)
        controller.setDirection(Direction.LEFT)

    concurrency.invoke_all([go_up, go_left], timeout_seconds=5)
    applied = str(controller.getDirection())
    assert_true(
        applied != "LEFT",
        "direction race: concurrent UP then LEFT from RIGHT produced LEFT "
        "(180-degree reverse within one tick)",
    )
