FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y curl build-essential && apt-get clean

# Устанавливаем Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Копируем только зависимости для установки
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости через Poetry и экспортируем их в requirements
RUN poetry export --without-hashes -f requirements.txt | pip install --no-cache-dir -r /dev/stdin

# Копируем остальной код
COPY . .

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
