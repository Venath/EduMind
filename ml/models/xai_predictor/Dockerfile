# Use official Python image
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
COPY src/ src/
COPY scripts/ scripts/
COPY config/ config/
COPY artifacts/ artifacts/
COPY data/ data/
RUN pip install --upgrade pip && pip install .[dev]

# Set environment variables if needed
ENV PYTHONUNBUFFERED=1

# Default command (run API, CLI, or pipeline)
CMD ["python", "-m", "scripts.run_pipeline", "--step", "all"]