# Каталог дефектов

Все десять заданий относятся к конкурентному выполнению и не ломают сборку Maven.

| ID | Модуль | Наблюдаемый сбой | Заготовка |
|---|---|---|---|
| BUG-01 | `game.score.ScoreCounter` | Часть одновременных начислений не входит в итог | `python-tests/exercises/test_bug_01.py` |
| BUG-02 | `game.control.DirectionController` | За один тик возможно направление, противоположное старту тика | `python-tests/exercises/test_bug_02.py` |
| BUG-03 | `game.world.EntityRegistry` | ConcurrentModificationException при обходе и изменении | `python-tests/exercises/test_bug_03.py` |
| BUG-04 | `game.loop.GameLoop` | `stop()` не останавливает цикл за ограниченное время | `python-tests/exercises/test_bug_04.py` |
| BUG-05 | `game.food.FoodPlacer` | Одна клетка получает несколько размещений еды | `python-tests/exercises/test_bug_05.py` |
| BUG-06 | `game.engine.GameSession` | Обновление и чтение рекордов могут зависнуть | `python-tests/exercises/test_bug_06.py` |
| BUG-07 | `game.loop.PauseController` | Тик выполняется после применения `pause()` | `python-tests/exercises/test_bug_07.py` |
| BUG-08 | `game.score.HighScoreStore` | Параллельные `save` теряют строки | `python-tests/exercises/test_bug_08.py` |
| BUG-09 | `game.loop.GameService` | После `stop()` остаются активные задачи | `python-tests/exercises/test_bug_09.py` |
| BUG-10 | `game.collision.CollisionProcessor` | Смерть обрабатывается больше одного раза | `python-tests/exercises/test_bug_10.py` |

Студенческое описание — в `docs/student-guide.md`. Разбор для преподавателя — в `docs/instructor-guide.md` (локально, не публикуется).
