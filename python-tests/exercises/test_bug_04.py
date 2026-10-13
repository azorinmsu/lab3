import pytest


@pytest.fixture
def game_loop(jvm):
    return jvm.JClass("game.loop.GameLoop")()


@pytest.mark.timeout(30)
def test_bug_04_visibility(game_loop, concurrency, project_dir):
    """
    BUG-04: Проверить, что stop() останавливает игровой цикл за ограниченное время.

    Один поток выполняет GameLoop.run(), другой вызывает stop().
    Цикл должен завершиться.

    ВАЖНО: запускайте сценарий через concurrency.run_isolated.

    TODO:
    1. В отдельном процессе стартовать цикл (startFlag + run в потоке).
    2. Дождаться хотя бы одного тика, затем вызвать stop().
    3. Ограничить ожидание join/таймаутом.
    4. Проверить, что поток цикла завершился.

    Не используйте time.sleep как основной способ синхронизации.
    """
    assert game_loop.getTicks() == 0
    pytest.skip("TODO: implement concurrency assertions")
