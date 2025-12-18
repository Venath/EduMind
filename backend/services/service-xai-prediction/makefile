.PHONY: help install run test docker-build docker-run clean

help:
    @echo "Available commands:"
    @echo "  make install      - Install dependencies"
    @echo "  make run          - Run the service locally"
    @echo "  make test         - Run tests"
    @echo "  make docker-build - Build Docker image"
    @echo "  make docker-run   - Run Docker container"
    @echo "  make clean        - Clean cache and build files"

install:
    pip install -r requirements.txt

run:
    uvicorn app.main:app --reload --port 8000

test:
    pytest tests/ -v --cov=app

docker-build:
    docker build -t edumind-xai-service .

docker-run:
    docker-compose up

docker-stop:
    docker-compose down

clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.log" -delete
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage

format:
    black app/
    isort app/

lint:
    flake8 app/