# Подготовка окружения

Репозиторий лаборатории: https://github.com/azorinmsu/lab3

Нужны:

- Java 17 (сборка идёт с исходников Java 8, запускается на JDK 17)
- Maven 3.8+
- Python 3.10+

## Установка

Из корня репозитория:

```bash
bash scripts/setup.sh
bash scripts/verify-environment.sh
```

`setup.sh` компилирует Java (`mvn -B -DskipTests compile`) и ставит зависимости из `python-tests/requirements.txt`: pytest, pytest-timeout, JPype1.

## Запуск игры

```bash
mvn -B -DskipTests compile
mvn exec:java
```

Управление: стрелки или WASD, пробел — новая игра.

## Запуск тестов

```bash
bash scripts/run-tests.sh
```

Отдельно:

```bash
mvn test
python3 -m pytest python-tests -q
```

Студенческие тесты `python-tests/exercises/test_bug_01.py` и `test_bug_06.py` в исходном виде пропускаются (`pytest.skip`), пока вы не замените заготовку.

Проверка преподавателя (эталонные тесты и патчи):

```bash
python3 instructor/validate_patches.py
```
