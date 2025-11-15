#!/bin/bash

echo "Creating project structure in current directory: $(pwd)"

# Root files
touch main.py
touch pyproject.toml
touch README.md

# agents directory
mkdir -p agents
touch agents/variants.py
touch agents/llm_client.py
touch agents/evaluator.py
touch agents/orchestrator.py

# sandbox directory
mkdir -p sandbox
touch sandbox/sandbox_runner.py

# mbpp directory
mkdir -p mbpp
touch mbpp/mbpp.jsonl
touch mbpp/mbpp_loader.py

# models directory
mkdir -p models
touch models/types.py

# results directory
mkdir -p results

# utils directory
mkdir -p utils
touch utils/code_extract.py
touch utils/timers.py
touch utils/cli_helpers.py

# tests directory
mkdir -p tests
touch tests/test_basic_flow.py

echo "Project scaffold created successfully!"
