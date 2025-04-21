# Coda Lite Makefile

.PHONY: setup dev-setup lint format test clean run help

# Default target
help:
	@echo "Coda Lite Makefile"
	@echo "=================="
	@echo "Available commands:"
	@echo "  make setup      - Install runtime dependencies"
	@echo "  make dev-setup  - Install development dependencies"
	@echo "  make lint       - Run linters (flake8, mypy)"
	@echo "  make format     - Run formatters (black, isort)"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make run        - Run Coda Lite"
	@echo "  make help       - Show this help message"

# Install runtime dependencies
setup:
	pip install -r requirements.txt

# Install development dependencies
dev-setup:
	pip install -r requirements-dev.txt
	pre-commit install

# Run linters
lint:
	flake8 .
	mypy .

# Run formatters
format:
	black .
	isort .

# Run tests
test:
	pytest -xvs

# Clean up temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/

# Run Coda Lite
run:
	python main.py
