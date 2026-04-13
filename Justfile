@default:
    just -l

# Code formatter
fmt:
    uvx ruff format

# Check formatting and types
check:
    uvx ruff check
    uvx ty check

# Run tests
test:
    uvx pytest