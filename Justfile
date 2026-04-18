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

# Make predictions using the agent
make_predictions *ARGS:
    uv run -m agent.make_predictions {{ARGS}}

# Evaluate predictions against the Spider dataset
eval *ARGS:
    uv run -m eval.evaluation {{ARGS}}

# Install dependencies
install:
    uv sync
    # Required nltk setup
    echo 'import nltk; nltk.download("punkt_tab")' | uv run -

# Download datasets
datasets: download-chinook download-spider

download-chinook:
    mkdir -p data
    wget -O data/Chinook.db https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db

download-spider:
    mkdir -p data
    uvx gdown -O data 'https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view'
    unzip data/spider_data.zip -d data
    rm data/spider_data.zip
    rm -rf data/__MACOSX
