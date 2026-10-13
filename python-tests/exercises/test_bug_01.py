import pytest


@pytest.fixture
def score_counter(jvm):
    counter = jvm.JClass("game.score.ScoreCounter")()
    counter.reset()
    return counter


def test_bug_01_concurrent_score(score_counter, concurrency):
    """
    BUG-01: Проверить корректность начисления очков при параллельном выполнении.

    Несколько потоков одновременно вызывают ScoreCounter.addPoints.
    Каждое начисление должно попасть в итоговый счёт.

    Для выравнивания потоков можно использовать CyclicBarrier и
    score_counter.setBeforeUpdate(...). В Java это удобно связать через
    game.lab.Barriers.arrive. Хук не меняет правило начисления:
    успешный вызов addPoints(n) обязан добавить ровно n очков.

    TODO:
    1. Организовать одновременное выполнение операций (барьер или latch).
    2. Выполнить конкурентные начисления.
    3. Дождаться завершения всех задач.
    4. Проверить итоговый счёт.

    Не используйте time.sleep как основной способ синхронизации.
    """
    threads = 8
    points = 1
    score_counter.reset()
    pytest.skip("TODO: implement concurrency assertions")
