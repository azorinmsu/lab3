import pytest


@pytest.fixture
def food_placer(jvm):
    return jvm.JClass("game.food.FoodPlacer")()


def test_bug_05_food_check_then_act(food_placer, concurrency, jvm):
    """
    BUG-05: Проверить, что одна клетка не получает две порции еды сразу.

    Несколько потоков одновременно вызывают FoodPlacer.place для одной клетки.
    Успешной должна быть только одна установка.

    Для выравнивания: setBetweenCheckAndPlace и game.lab.Barriers.arrive.

    TODO:
    1. Выровнять потоки барьером внутри place.
    2. Выполнить конкурентные place(x, y) с одинаковыми координатами.
    3. Дождаться завершения.
    4. Проверить число успешных place и size().

    Не используйте time.sleep как основной способ синхронизации.
    """
    pytest.skip("TODO: implement concurrency assertions")
