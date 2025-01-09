FROM python:3.12-slim

RUN mkdir -p /app && addgroup --gid 10001 app && \
    adduser --uid 10001 --gid 10001 --home /app app && \
    chmod 755 /app

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY slack_notifier /app

RUN chown -R app:app /app

USER app

ENTRYPOINT ["python", "-m", "typer", "app.main", "run"]
