# List available commands
@default:
    just -l

# Code formatter
fmt:
    uvx ruff format

# Check formatting, linter and types
check:
    uvx ruff format --check
    uvx ruff check
    uvx ty check

# Run tests
test:
    uvx pytest

# Run agent demo
agent:
    uv run -m agent.agent

# Download datasets
datasets:
    wget -O data/Chinook.db https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db