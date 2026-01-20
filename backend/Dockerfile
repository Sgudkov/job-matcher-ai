# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Установка системных пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_HOME="/opt/poetry" \
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip

COPY pyproject.toml ./
COPY whl/torch-2.4.1+cpu-cp312-cp312-linux_x86_64.whl ./whl/

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry
RUN poetry add whl/torch-2.4.1+cpu-cp312-cp312-linux_x86_64.whl

# Установка deps
RUN poetry install --no-root --no-interaction --no-ansi

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
# --- Stage 2: Runtime ---
FROM python:3.12-slim AS runtime

RUN useradd -m appuser
USER appuser

# Копируем виртуальное окружение из builder-образа
COPY --from=builder /app/.venv /app/.venv

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
