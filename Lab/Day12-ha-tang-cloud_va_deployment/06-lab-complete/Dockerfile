# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

RUN groupadd -r agent && useradd -r -g agent -d /app agent

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY src/ ./src/
COPY start.sh ./start.sh

RUN chown -R agent:agent /app /opt/venv && chmod +x /app/start.sh

USER agent

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; p=os.getenv('PORT', '8080'); urllib.request.urlopen(f'http://localhost:{p}/')" \
    || exit 1

CMD ["sh", "start.sh"]
