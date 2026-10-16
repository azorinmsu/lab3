import pytest

from helpers.assertions import assert_equal, assert_true


def test_bug_08_concurrent_persistence(concurrency, jvm, tmp_path):
    """Parallel save() calls must persist every line in a valid format."""
    Barriers = jvm.JClass("game.lab.Barriers")
    path = tmp_path / "scores.txt"
    store = jvm.JClass("game.score.HighScoreStore")(jvm.JClass("java.nio.file.Paths").get(str(path)))
    threads = 8
    barrier = concurrency.cyclic_barrier(threads)
    store.setBeforeWrite(Barriers.arrive(barrier))

    def save_one(index):
        store.save("P" + str(index), index + 1)

    concurrency.invoke_all(
        [lambda i=i: save_one(i) for i in range(threads)],
        timeout_seconds=10,
    )

    lines = [str(line) for line in store.readAll() if str(line).strip()]
    assert_equal(
        len(lines),
        threads,
        "concurrent persistence: not every confirmed save was stored intact",
    )
    for line in lines:
        assert_true(
            ":" in line and not line.startswith(":"),
            f"concurrent persistence: malformed score line {line!r}",
        )
