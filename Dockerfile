FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential libpq-dev

RUN pip install poetry

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

ENV PATH="/app/.venv/bin:$PATH"