# Makefile for ambient-expense-agent

.PHONY: install playground lint test run-auto run-review

# Install dependencies using uv sync
install:
	uv sync

# Launch the ADK local web playground
playground:
	uv run python expense_agent/fast_api_app.py

# Check code format and type constraints
lint:
	agents-cli lint --fix

# Run unit and integration tests
test:
	uv run pytest

# Test the auto-approval path (< $100)
run-auto:
	agents-cli run "{\"data\": {\"amount\": 50.0, \"submitter\": \"bob@company.com\", \"category\": \"meals\", \"description\": \"Client dinner\", \"date\": \"2026-06-06\"}}"

# Test the manual review path (>= $100)
run-review:
	agents-cli run "{\"data\": {\"amount\": 150.0, \"submitter\": \"alice@company.com\", \"category\": \"software\", \"description\": \"IDE License\", \"date\": \"2026-06-06\"}}"
