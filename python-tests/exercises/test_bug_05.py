import pytest

from helpers.assertions import assert_equal


def test_bug_05_food_check_then_act(concurrency, jvm):
    """Only one concurrent place() for the same cell may succeed."""
    Barriers = jvm.JClass("game.lab.Barriers")
    placer = jvm.JClass("game.food.FoodPlacer")()
    barrier = concurrency.cyclic_barrier(2)
    placer.setBetweenCheckAndPlace(Barriers.arrive(barrier))

    def place_once():
        return bool(placer.place(3, 4))

    results = concurrency.invoke_all([place_once, place_once], timeout_seconds=5)
    success = sum(1 for value in results if value)
    assert_equal(
        success,
        1,
        "check-then-act: concurrent place() on one cell succeeded more than once",
    )
    assert_equal(int(placer.size()), 1, "check-then-act: occupied cell count")
