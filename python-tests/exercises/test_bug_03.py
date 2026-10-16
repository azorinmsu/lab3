import pytest

from helpers.assertions import assert_true


def test_bug_03_unsafe_collection(concurrency, jvm):
    """Concurrent mutate + iterate must not throw ConcurrentModificationException."""
    Entity = jvm.JClass("game.world.Entity")
    Barriers = jvm.JClass("game.lab.Barriers")
    registry = jvm.JClass("game.world.EntityRegistry")()
    for i in range(100):
        registry.add(Entity("seed-" + str(i)))

    ready = concurrency.cyclic_barrier(2)
    iterator_ready = concurrency.countdown_latch(1)
    registry.setBeforeIterate(Barriers.arrive(ready))
    registry.setBeforeMutate(Barriers.arrive(ready))

    errors = []

    def iterate():
        try:
            view = registry.view()
            registry.setBeforeIterate(None)
            it = view.iterator()
            iterator_ready.countDown()
            while it.hasNext():
                it.next()
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))

    def mutate():
        try:
            registry.add(Entity("racer-0"))
            registry.setBeforeMutate(None)
            concurrency.await_latch(iterator_ready)
            for i in range(1, 50):
                registry.add(Entity("racer-" + str(i)))
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))

    concurrency.invoke_all([iterate, mutate], timeout_seconds=5)

    cme = [err for err in errors if "ConcurrentModificationException" in err]
    assert_true(
        len(cme) == 0,
        "unsafe collection: ConcurrentModificationException during concurrent "
        f"iterate/mutate: {cme!r}",
    )
