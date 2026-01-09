# Тесты для проекта pro_accounter

## Установка зависимостей

Перед запуском тестов установите необходимые зависимости:

```bash
pip install -r requirements.txt
```

Или установите только тестовые зависимости:

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

## Запуск тестов

### Запуск всех тестов

```bash
pytest
```

### Запуск с покрытием кода

```bash
pytest --cov=. --cov-report=term-missing --cov-report=html
```

### Запуск конкретного файла тестов

```bash
pytest tests/test_validators.py
```

### Запуск с подробным выводом

```bash
pytest -v
```

## Структура тестов

- `test_validators.py` - тесты для валидаторов (валидация телефонов)
- `test_excel.py` - тесты для генерации Excel отчетов
- `test_plots.py` - тесты для построения графиков
- `test_models.py` - тесты для Pydantic моделей
- `test_db.py` - тесты для работы с базой данных (с моками)
- `test_config.py` - тесты для конфигурации
- `test_handlers_*.py` - тесты для обработчиков (handlers)

## Покрытие кода

Целевое покрытие: **80%**

После запуска тестов с флагом `--cov-report=html` будет создана папка `htmlcov` с детальным отчетом о покрытии.

## Примечания

- Все тесты используют моки для изоляции от внешних зависимостей (база данных, aiogram)
- Асинхронные тесты используют `pytest-asyncio`
- Тесты для handlers используют моки для aiogram компонентов



