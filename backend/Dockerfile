FROM python:3.12-slim

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false

# Установка системных пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip


COPY pyproject.toml ./
COPY whl/torch-2.4.1+cpu-cp312-cp312-linux_x86_64.whl ./whl/

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry
RUN poetry add whl/torch-2.4.1+cpu-cp312-cp312-linux_x86_64.whl


# Установка deps
RUN poetry install --no-root --no-interaction --no-ansi


COPY . .

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
