#!/bin/bash
# Coda Lite run script

# Make script exit on first error
set -e

# Function to display help
show_help() {
    echo "Coda Lite Run Script"
    echo "===================="
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  setup      - Install runtime dependencies"
    echo "  dev-setup  - Install development dependencies"
    echo "  lint       - Run linters (flake8, mypy)"
    echo "  format     - Run formatters (black, isort)"
    echo "  test       - Run tests"
    echo "  clean      - Clean up temporary files"
    echo "  run        - Run Coda Lite"
    echo "  help       - Show this help message"
    echo ""
    echo "If no command is provided, 'run' is executed by default."
}

# Function to install runtime dependencies
setup() {
    echo "Installing runtime dependencies..."
    pip install -r requirements.txt
}

# Function to install development dependencies
dev_setup() {
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
    pre-commit install
}

# Function to run linters
lint() {
    echo "Running linters..."
    flake8 .
    mypy .
}

# Function to run formatters
format() {
    echo "Running formatters..."
    black .
    isort .
}

# Function to run tests
test() {
    echo "Running tests..."
    pytest -xvs
}

# Function to clean up temporary files
clean() {
    echo "Cleaning up temporary files..."
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
}

# Function to run Coda Lite
run() {
    echo "Running Coda Lite..."
    python main.py
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    # No arguments provided, run by default
    run
else
    case "$1" in
        setup)
            setup
            ;;
        dev-setup)
            dev_setup
            ;;
        lint)
            lint
            ;;
        format)
            format
            ;;
        test)
            test
            ;;
        clean)
            clean
            ;;
        run)
            run
            ;;
        help)
            show_help
            ;;
        *)
            echo "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
fi
