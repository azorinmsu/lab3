# Руководство студента

Лабораторная проверяет умение описать конкурентный сценарий и поймать нарушение инварианта. Десять заданий: BUG-01 … BUG-10.

Исправление ищется тестом. В заготовках нет готовых assertions. Эталонные тесты и патчи у преподавателя.

## Общий порядок

1. Прочитайте `docs/setup.md` и выполните `bash scripts/setup.sh`.
2. Откройте заготовку в `python-tests/exercises/`.
3. Уберите `pytest.skip` и реализуйте сценарий.
4. Запустите тест:

```bash
python3 -m pytest python-tests/exercises/test_bug_XX.py -q
```

5. Исправьте Java-код по результатам теста.
6. Убедитесь, что `mvn test` и игра собираются.

Не используйте `time.sleep` как основной способ синхронизации. Для барьера и защёлки: `concurrency.cyclic_barrier`, `countdown_latch`, `await_barrier`, `await_latch`. В JPype методы Java `await` доступны как `await_`.

JVM поднимается один раз на сессию. Сценарии с возможным зависанием (BUG-04, BUG-06, BUG-09) запускайте через `concurrency.run_isolated`.

## Задания

### BUG-01. Потерянные начисления

`ScoreCounter.addPoints` при параллельных вызовах. Итог = сумма всех начислений. Хук: `setBeforeUpdate` + `game.lab.Barriers.arrive`.

### BUG-02. Гонка направления

`DirectionController`: после `beginTick()` конкурентные `setDirection` не должны установить направление, противоположное `tickStart`.

### BUG-03. Небезопасная коллекция

`EntityRegistry`: одновременные `view()`/обход и `add()` без `ConcurrentModificationException`. Хуки: `setBeforeIterate`, `setBeforeMutate`.

### BUG-04. Видимость stop

`GameLoop`: поток в `run()`, другой вызывает `stop()` — цикл завершается. Только через `run_isolated`.

### BUG-05. Check-then-act для еды

`FoodPlacer.place` на одну клетку: успешен ровно один вызов. Хук: `setBetweenCheckAndPlace`.

### BUG-06. Deadlock игры и рекордов

`GameSession.updateAndRecord` и `readRecordsAndState` завершаются за ограниченное время. В заготовке есть `WORKER` до `newFixedThreadPool(2)`; допишите сценарий и вызов `run_isolated`.

### BUG-07. Pause / resume

`PauseController`: если `pause()` применён до решения о тике, `tryTick` не увеличивает счётчик. Хуки: `setBeforePause`, `setBeforeTickDecision`.

### BUG-08. Конкурентная запись рекордов

`HighScoreStore.save` в временный файл: все строки на месте, формат `player:points`. Хук: `setBeforeWrite`.

### BUG-09. Утечка потоков

`GameService`: несколько `start()`, затем `stop()` — `awaitIdle` и ноль активных задач. Только через `run_isolated`.

### BUG-10. Двойная обработка столкновения

`CollisionProcessor.handleCollision`: ровно одно событие смерти и одно начисление. Хук: `setBeforeMarkDead`.

## Критерии оценки

См. `instructor/grading.md`. Кратко: реальный конкурентный сценарий, проверка инварианта, устойчивое воспроизведение, синхронизация без произвольных пауз, понятная диагностика, читаемый pytest.
