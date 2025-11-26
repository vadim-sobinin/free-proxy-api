# Build stage with Alpine
FROM python:3.11-alpine as builder

WORKDIR /build

COPY requirements.txt .

# Install build dependencies and dependencies for lxml + Rust for ARM
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    libxml2-dev \
    libxslt-dev \
    rust \
    cargo \
    && pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt \
    && apk del .build-deps

# Clean build artifacts in builder
RUN find /root/.local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -type f -name "*.pyc" -delete \
    && find /root/.local -type f -name "*.pyo" -delete \
    && find /root/.local/lib/python*/site-packages -type d -name tests -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local/lib/python*/site-packages -type d -name "*.dist-info" ! -name "pydantic*" -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local/lib/python*/site-packages -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -type f \( -name "*.txt" -o -name "*.md" -o -name "RECORD" \) -delete 2>/dev/null || true \
    && find /root/.local -type f -name "*.so" -exec strip -s {} \; 2>/dev/null || true \
    && rm -rf /root/.local/lib/python*/site-packages/pip /root/.local/lib/python*/site-packages/setuptools 2>/dev/null || true

# Runtime stage
FROM python:3.11-alpine AS runtime

WORKDIR /app

# Install only runtime dependencies
RUN apk add --no-cache curl libxml2 libxslt

# Copy compiled packages from builder
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy only essential app files
COPY main.py .
COPY fp ./fp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
