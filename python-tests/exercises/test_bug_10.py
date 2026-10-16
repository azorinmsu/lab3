import pytest

from helpers.assertions import assert_equal


def test_bug_10_double_collision(concurrency, jvm):
    """Parallel handleCollision for one snake must run at most once."""
    Barriers = jvm.JClass("game.lab.Barriers")
    processor = jvm.JClass("game.collision.CollisionProcessor")()
    barrier = concurrency.cyclic_barrier(2)
    processor.setBeforeMarkDead(Barriers.arrive(barrier))

    def hit():
        processor.handleCollision(5)

    concurrency.invoke_all([hit, hit], timeout_seconds=5)

    assert_equal(
        int(processor.getDeathEvents()),
        1,
        "double collision: death event processed more than once",
    )
    assert_equal(
        int(processor.getScoreAwarded()),
        5,
        "double collision: score awarded more than once",
    )
    assert processor.isDead()
