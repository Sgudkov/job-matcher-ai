# ============================================================================
# УСТАНОВКА И НАСТРОЙКА
# ============================================================================

install:
	poetry install --no-root

setup: install
	poetry run pre-commit install


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================

test:
	poetry run pytest app/tests/ -v

test-all:
	poetry run pytest app/tests/test_api.py -v

test-auth:
	poetry run pytest app/tests/test_api.py::TestAuth -v

test-candidates:
	poetry run pytest app/tests/test_api.py::TestCandidates -v

test-employers:
	poetry run pytest app/tests/test_api.py::TestEmployers -v

test-resumes:
	poetry run pytest app/tests/test_api.py::TestResumes -v

test-vacancies:
	poetry run pytest app/tests/test_api.py::TestVacancies -v

test-matches:
	poetry run pytest app/tests/test_api.py::TestMatches -v

test-integration:
	poetry run pytest app/tests/test_api.py::TestIntegration -v

test-cov:
	poetry run pytest app/tests/ --cov=backend.app --cov-report=html --cov-report=term

test-watch:
	poetry run pytest-watch app/tests/ -v


# ============================================================================
# МИГРАЦИИ БАЗЫ ДАННЫХ (ALEMBIC)
# ============================================================================

alembic-revision:
	poetry run alembic -c alembic.ini revision --autogenerate -m "init tables"

alembic-upgrade:
	poetry run alembic -c alembic.ini upgrade head

alembic-downgrade:
	poetry run alembic -c alembic.ini downgrade -1

alembic-current:
	poetry run alembic -c alembic.ini current

alembic-history:
	poetry run alembic -c alembic.ini history


# ============================================================================
# КАЧЕСТВО КОДА
# ============================================================================

pre-commit:
	poetry run pre-commit run --all-files

lint:
	poetry run ruff check

lint-fix:
	poetry run ruff check --fix

format:
	poetry run black

format-check:
	poetry run black --check


# ============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================================================

run:
	poetry run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	poetry run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4


# ============================================================================
# ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ
# ============================================================================

load-data:
	poetry run python -m backend.app.utils.generator_test_data

load-data-fresh:
	@echo "Очистка БД и загрузка свежих данных..."
	$(MAKE) down
	$(MAKE) up
	$(MAKE) load-data

clear-qdrant:
	poetry run python -m backend.app.utils.generator_test_data --clear-qdrant


# ============================================================================
# ОЧИСТКА
# ============================================================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage


# ============================================================================
# DOCKER
# ============================================================================

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart


# ============================================================================
# СОКРАЩЕНИЯ (ALIASES)
# ============================================================================

rev: alembic-revision
up: alembic-upgrade
down: alembic-downgrade
curr: alembic-current
hist: alembic-history


# ============================================================================
# HELP
# ============================================================================

help:
	@echo "=== Job Matcher AI - Makefile Commands ==="
	@echo ""
	@echo "УСТАНОВКА:"
	@echo "  make install          - Установить зависимости"
	@echo "  make setup            - Установить зависимости + pre-commit hooks"
	@echo ""
	@echo "ТЕСТИРОВАНИЕ:"
	@echo "  make test             - Запустить все тесты"
	@echo "  make test-all         - Запустить все API тесты"
	@echo "  make test-auth        - Тесты аутентификации"
	@echo "  make test-candidates  - Тесты кандидатов"
	@echo "  make test-employers   - Тесты работодателей"
	@echo "  make test-cov         - Тесты с покрытием кода"
	@echo ""
	@echo "МИГРАЦИИ:"
	@echo "  make rev              - Создать новую миграцию"
	@echo "  make up               - Применить миграции"
	@echo "  make down             - Откатить последнюю миграцию"
	@echo "  make curr             - Текущая версия БД"
	@echo ""
	@echo "КАЧЕСТВО КОДА:"
	@echo "  make lint             - Проверить код (ruff)"
	@echo "  make format           - Форматировать код (black)"
	@echo "  make pre-commit       - Запустить pre-commit hooks"
	@echo ""
	@echo "ЗАПУСК:"
	@echo "  make run              - Запустить dev сервер"
	@echo "  make run-prod         - Запустить prod сервер"
	@echo ""
	@echo "ТЕСТОВЫЕ ДАННЫЕ:"
	@echo "  make load-data        - Загрузить тестовые данные из JSON"
	@echo "  make load-data-fresh  - Очистить БД и загрузить свежие данные"
	@echo "  make clear-qdrant     - Очистить данные из Qdrant"
	@echo ""
	@echo "DOCKER:"
	@echo "  make docker-up        - Запустить Docker контейнеры"
	@echo "  make docker-down      - Остановить Docker контейнеры"
	@echo ""
	@echo "ОЧИСТКА:"
	@echo "  make clean            - Удалить кэш и временные файлы"

.PHONY: install setup test test-all test-auth test-candidates test-employers \
        test-resumes test-vacancies test-matches test-integration test-cov \
        alembic-revision alembic-upgrade alembic-downgrade alembic-current \
        alembic-history pre-commit lint lint-fix format format-check run \
        run-prod load-data load-data-fresh clear-qdrant clean docker-build \
        docker-up docker-down docker-logs docker-restart help rev up down curr hist
