FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install uv && uv sync

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "eventflow:app", "--host", "0.0.0.0", "--port", "8000"]