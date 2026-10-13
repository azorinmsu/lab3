import pytest


@pytest.fixture
def entity_registry(jvm):
    return jvm.JClass("game.world.EntityRegistry")()


def test_bug_03_unsafe_collection(entity_registry, concurrency, jvm):
    """
    BUG-03: Проверить безопасную работу с коллекцией игровых объектов.

    Один поток вызывает snapshotIds(), другой одновременно add(...).
    Не должно быть ConcurrentModificationException и потери согласованности.

    Для выравнивания: setBeforeIterate / setBeforeMutate и game.lab.Barriers.arrive.

    TODO:
    1. Подготовить несколько объектов в реестре.
    2. Одновременно запустить обход и изменение.
    3. Дождаться завершения.
    4. Убедиться, что исключения гонки коллекции нет и состояние осмысленно.

    Не используйте time.sleep как основной способ синхронизации.
    """
    Entity = jvm.JClass("game.world.Entity")
    pytest.skip("TODO: implement concurrency assertions")
