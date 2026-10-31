# Multi-stage: builder installs deps, runtime is slim + non-root (MLOps minimum viable)
FROM python:3.11.18-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies to site-packages
RUN python -m pip install --no-cache-dir --upgrade pip==26.2.2 \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && rm -rf /install/lib/python3.11/site-packages/pillow-*.dist-info \
    && pip install --no-cache-dir --prefix=/install --no-deps Pillow==13.0.0

# Runtime stage with security hardening
FROM python:3.11.18-slim-bookworm AS runtime

# Security: Update system packages to latest patches
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

RUN find /usr/local/lib/python3.11/site-packages -maxdepth 1 \
    \( -name 'pip' -o -name 'pip-*' -o -name 'setuptools' -o -name 'setuptools-*' \
    -o -name 'wheel' -o -name 'wheel-*' \) -exec rm -rf '{}' + \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.11

# Copy application code
COPY api ./api
COPY app ./app
COPY common ./common
COPY batch ./batch
COPY monitoring ./monitoring
COPY models ./models

# Security: Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
