# AWS Account Automation Project

# Install dependencies
install:
    uv sync --extra dev

# Run linting
lint:
    uv run ruff check .

# Fix linting issues
lint-fix:
    uv run ruff check --fix .

# Run type checking
typecheck:
    uv run mypy . --ignore-missing-imports

# Run tests
test:
    uv run python test_basic.py

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Create AWS account with configuration file
create-account config_file="sample_config.json":
    uv run python aws_creator.py {{config_file}}

# Validate configuration file
validate config_file="sample_config.json":
    uv run python -c "import json; json.load(open('{{config_file}}'))"

# Clean up generated files
clean:
    rm -f *.png *.log
    rm -rf __pycache__ .mypy_cache .ruff_cache .pytest_cache

# Show project status
status:
    @echo "=== AWS Account Automation Project ==="
    @echo "✅ Basic AWS account creator implemented"
    @echo "✅ Browser automation with Selenium"
    @echo "✅ Configuration management"
    @echo "✅ Testing framework"
    @echo ""
    @echo "Commands:"
    @echo "  just install       - Install dependencies"
    @echo "  just check         - Run all checks"
    @echo "  just create-account - Create AWS account"
    @echo "  just test          - Run tests"