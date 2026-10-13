import pytest


@pytest.fixture
def collision_processor(jvm):
    return jvm.JClass("game.collision.CollisionProcessor")()


def test_bug_10_double_collision(collision_processor, concurrency, jvm):
    """
    BUG-10: Проверить at-most-once обработку столкновения.

    Два потока одновременно вызывают handleCollision для одной змейки.
    Событие смерти и начисление должны выполниться ровно один раз.

    Для выравнивания: setBeforeMarkDead и game.lab.Barriers.arrive.

    TODO:
    1. Выровнять два вызова handleCollision.
    2. Дождаться завершения.
    3. Проверить getDeathEvents() == 1 и корректный scoreAwarded.

    Не используйте time.sleep как основной способ синхронизации.
    """
    pytest.skip("TODO: implement concurrency assertions")
