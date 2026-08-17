# Shipwright Evidence Ledger direction: small, inspectable, secure runtime image.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY shipwright_core ./shipwright_core
COPY shipwright.toml ./shipwright.toml

RUN python -m pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 shipwright \
    && chown -R shipwright:shipwright /app

USER shipwright
ENTRYPOINT ["shipwright"]
CMD ["inspect", ".", "--format", "markdown"]
