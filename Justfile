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
    uv run pytest

# Run agent demo
agent *ARGS:
    uv run -m agent.agent {{ARGS}}

# Make predictions using the agent
make_predictions *ARGS:
    uv run -m agent.make_predictions {{ARGS}}

# Make predictions and save terminal output to logs/<name>_<timestamp>.log
make_predictions_logged LOG_NAME *ARGS:
    mkdir -p logs results
    bash -o pipefail -c 'if [ "${1:-}" = "--" ]; then shift; fi; uv run -m agent.make_predictions "$@" 2>&1 | tee "logs/{{LOG_NAME}}_$(date +%Y%m%d_%H%M%S).log"' -- {{ARGS}}

# Evaluate predictions against the Spider dataset
eval *ARGS:
    uv run -m eval.evaluation {{ARGS}}

# Evaluate predictions and save terminal output to logs/<name>_<timestamp>.log
eval_logged LOG_NAME *ARGS:
    mkdir -p logs results
    bash -o pipefail -c 'if [ "${1:-}" = "--" ]; then shift; fi; uv run -m eval.evaluation "$@" 2>&1 | tee "logs/{{LOG_NAME}}_$(date +%Y%m%d_%H%M%S).log"' -- {{ARGS}}

# Create per-example evaluation report without creating an extra log file
diagnostic_report_logged LOG_NAME *ARGS:
    mkdir -p results
    bash -o pipefail -c 'if [ "${1:-}" = "--" ]; then shift; fi; uv run -m eval.diagnostic_report "$@"' -- {{ARGS}}

# Build data/spider_data/manual_test.json from data/spider_data/manual_test_indices.txt
manual_subset:
    uv run python scripts/build_manual_subset.py

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
