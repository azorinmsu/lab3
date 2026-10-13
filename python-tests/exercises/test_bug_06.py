import pytest

WORKER = r"""
import os
import sys
import traceback
from pathlib import Path

root = Path(os.environ["SNAKE_PROJECT_ROOT"])
sys.path.insert(0, str(root / "python-tests"))

from helpers.jvm import ensure_jvm

jpype = ensure_jvm()
JClass = jpype.JClass


def halt(code):
    jpype.java.lang.Runtime.getRuntime().halt(code)


def main():
    session = JClass("game.engine.GameSession")()
    barrier = JClass("java.util.concurrent.CyclicBarrier")(2)
    hook = JClass("game.lab.Barriers").arrive(barrier)
    session.setAfterEngineLockAcquired(hook)
    session.setAfterScoreLockAcquired(hook)

    executors = JClass("java.util.concurrent.Executors")
    time_unit = JClass("java.util.concurrent.TimeUnit")
    timeout_type = JClass("java.util.concurrent.TimeoutException")
    executor = executors.newFixedThreadPool(2)

    # TODO:
    # 1. Оформите два Callable: один вызывает updateAndRecord("Ada", 10),
    #    другой вызывает readRecordsAndState().
    # 2. Отправьте оба задания в executor и дождитесь Future.get
    #    с ограничением времени (используйте time_unit и timeout_type).
    # 3. При таймауте запишите в stderr сообщение про deadlock и завершите
    #    процесс через halt(2).
    # 4. После успешного завершения проверьте согласованность:
    #    ticks == 1, score == 10, records == ["Ada:10"].
    #    При нарушении — сообщение в stderr и halt(1).
    # 5. При успехе напишите "ok" в stdout и вызовите halt(0).
    #
    # Не используйте time.sleep как основной способ синхронизации.
    raise NotImplementedError("TODO: implement concurrent update/read scenario")


try:
    main()
except BaseException:
    traceback.print_exc()
    halt(1)
"""


@pytest.fixture
def game_session(jvm):
    return jvm.JClass("game.engine.GameSession")()


@pytest.mark.timeout(30)
def test_bug_06_no_deadlock(game_session, concurrency, project_dir):
    """
    BUG-06: Проверить, что обновление игры и чтение рекордов завершаются.

    Один поток вызывает GameSession.updateAndRecord, другой одновременно
    вызывает GameSession.readRecordsAndState. Обе операции должны закончиться
    за ограниченное время, а после этого состояние сессии должно быть согласованным:
    одно подтверждённое начисление, одна запись рекорда.

    WORKER уже поднимает JVM, создаёт GameSession, выравнивает потоки через
    CyclicBarrier и хуки setAfterEngineLockAcquired / setAfterScoreLockAcquired,
    готовит ExecutorService. Допишите сценарий внутри WORKER.main после
    создания пула потоков.

    ВАЖНО: сценарий с возможной взаимной блокировкой запускайте через
    concurrency.run_isolated, чтобы зависший Java-поток не остановил pytest.

    TODO:
    1. Завершите реализацию WORKER.main (см. TODO внутри WORKER).
    2. Запустите WORKER через concurrency.run_isolated с таймаутом.
    3. Убедитесь, что дочерний процесс завершился с кодом 0.
    4. При ненулевом коде покажите stdout/stderr в сообщении assertion.

    Не используйте time.sleep как основной способ синхронизации.
    """
    assert game_session.getTicks() == 0
    pytest.skip("TODO: implement concurrency assertions")
