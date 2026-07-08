# syntax=docker/dockerfile:1

# ---- Builder stage -------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

# Build a wheel and install it (plus deps) into an isolated prefix.
RUN python -m pip install --upgrade pip build \
    && python -m build --wheel --outdir /wheels \
    && pip install --prefix=/install /wheels/*.whl

# ---- Runtime stage -------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FEATURE_STORE_HOST=0.0.0.0 \
    FEATURE_STORE_PORT=8000

# Create an unprivileged user to run the service.
RUN groupadd --system app && useradd --system --gid app --home /app app

COPY --from=builder /install /usr/local

WORKDIR /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else sys.exit(1)"

CMD ["uvicorn", "feature_store.main:app", "--host", "0.0.0.0", "--port", "8000"]
