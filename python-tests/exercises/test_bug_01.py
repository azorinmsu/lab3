import pytest

from helpers.assertions import assert_equal


@pytest.fixture
def score_counter(jvm):
    counter = jvm.JClass("game.score.ScoreCounter")()
    counter.reset()
    return counter


def test_bug_01_concurrent_score(score_counter, concurrency, jvm):
    """Every concurrent addPoints call is included in the final score."""
    threads = 8
    points = 1
    score_counter.reset()

    barrier = concurrency.cyclic_barrier(threads)
    score_counter.setBeforeUpdate(jvm.JClass("game.lab.Barriers").arrive(barrier))

    def add_once():
        score_counter.addPoints(points)

    concurrency.invoke_all([add_once for _ in range(threads)], timeout_seconds=10)

    expected = threads * points
    actual = int(score_counter.getScore())
    assert_equal(
        actual,
        expected,
        "lost update: concurrent score increments were not all applied",
    )
