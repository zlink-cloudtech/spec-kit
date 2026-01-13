# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip build

# Build wheel
RUN python -m build

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy built wheel from builder
COPY --from=builder /app/dist/*.whl .

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install the package
RUN python -m pip install --no-cache-dir *.whl

# Copy source code (optional if included in wheel, but good for direct running if needed, though wheel should suffice)
# We will rely on the installed package.

# Create data directory with correct permissions
RUN mkdir -p /data && chown -R appuser:appuser /data

USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV STORAGE_PATH=/data
ENV CONFIG_PATH=/app/config.yaml

EXPOSE 8000

# Command to run
CMD ["uvicorn", "release_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
