import pytest


def test_bug_08_concurrent_persistence(concurrency, jvm, tmp_path):
    """
    BUG-08: Проверить конкурентную запись таблицы рекордов.

    Несколько потоков одновременно вызывают HighScoreStore.save.
    Все строки должны сохраниться, формат player:points должен остаться целым.

    Для выравнивания: setBeforeWrite и game.lab.Barriers.arrive.
    Файл создавайте через tmp_path.

    TODO:
    1. Создать HighScoreStore на временном файле.
    2. Выполнить параллельные save.
    3. Дождаться завершения.
    4. Прочитать файл и проверить число и формат строк.

    Не используйте time.sleep как основной способ синхронизации.
    """
    pytest.skip("TODO: implement concurrency assertions")
