FROM python:3.11-slim
WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple
ENV PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=5 \
    PIP_INDEX_URL=${PIP_INDEX_URL}

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app
RUN mkdir -p /app/uploads /app/data
ENV NJU_DB_URL=sqlite:////app/data/nju.db \
    NJU_UPLOAD_DIR=/app/uploads
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
