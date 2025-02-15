FROM python:3.8-slim

COPY . .

RUN pip install -r requirements.txt

WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]