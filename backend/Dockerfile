# Multi-stage Dockerfile for Quant Backend Service
# Optimized for size and performance with UV package manager

#######################
# Stage 1: Dependencies
#######################
FROM python:3.12-slim AS dependencies

WORKDIR /app/
# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libgomp1 \
    && pip install --no-cache-dir uv==0.4.18 \
    && rm -rf /var/lib/apt/lists/*

# Copy project configuration files (for better layer caching)
COPY ./pyproject.toml ./uv.lock ./


#######################
# Stage 2: Builder
#######################
FROM dependencies AS builder

# Copy application source code
COPY ./app ./app


# Create virtual environment and install dependencies
RUN uv venv .venv
ENV PATH="/app/.venv/bin:$PATH"

# Install project and its dependencies (production only, no dev dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Clean up unnecessary files to reduce image size
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true && \
    find /app -name "*.pyo" -delete && \
    find /app -name "tests" -type d -exec rm -rf {} + || true && \
    find /app -name ".pytest_cache" -type d -exec rm -rf {} + || true && \
    find /app -name ".ruff_cache" -type d -exec rm -rf {} + || true

#######################
# Stage 3: Runtime
#######################
FROM python:3.12-slim AS runtime

# Install runtime dependencies and create user
RUN apt-get update && apt-get install -y \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser


# Copy virtual environment and source code from builder
COPY --from=builder /app/.venv /.venv
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000


# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
