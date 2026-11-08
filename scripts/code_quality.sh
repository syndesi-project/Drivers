#!/usr/bin/env bash
set -e

echo "Running Ruff (lint + fix)..."
ruff check --fix syndesi_drivers

echo "Running isort..."
isort syndesi_drivers

echo "Running Black..."
black syndesi_drivers

echo "Running mypy..."
mypy syndesi_drivers

echo "Running Bandit..."
bandit -r syndesi_drivers

echo "Running Pylint..."
pylint syndesi_drivers
