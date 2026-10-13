import pytest


@pytest.fixture
def direction_controller(jvm):
    return jvm.JClass("game.control.DirectionController")()


def test_bug_02_direction_race(direction_controller, concurrency, jvm):
    """
    BUG-02: Проверить, что конкурентные команды управления не дают
    разворот на 180 градусов за один игровой тик.

    DirectionController.beginTick() фиксирует направление на старте тика.
    Параллельные setDirection не должны установить направление, противоположное
    tickStart.

    TODO:
    1. Вызвать beginTick().
    2. Одновременно отправить допустимую и противоположную исходному направлению команды.
    3. Дождаться завершения задач.
    4. Проверить, что итог не является разворотом на 180 градусов.

    Не используйте time.sleep как основной способ синхронизации.
    """
    Direction = jvm.JClass("game.control.Direction")
    direction_controller.beginTick()
    pytest.skip("TODO: implement concurrency assertions")
