import pytest


@pytest.fixture
def game_service(jvm):
    return jvm.JClass("game.loop.GameService")()


@pytest.mark.timeout(30)
def test_bug_09_thread_leak(game_service, concurrency, project_dir):
    """
    BUG-09: Проверить отсутствие утечки игровых задач после stop().

    Многократный start() создаёт фоновые задачи. После stop() активных задач
    быть не должно.

    ВАЖНО: запускайте сценарий через concurrency.run_isolated.

    TODO:
    1. В отдельном процессе несколько раз вызвать start().
    2. Вызвать stop().
    3. Дождаться idle с таймаутом (awaitIdle).
    4. Проверить, что active tasks == 0.

    Не используйте time.sleep как основной способ синхронизации.
    """
    assert game_service.getActiveTasks() == 0
    pytest.skip("TODO: implement concurrency assertions")
