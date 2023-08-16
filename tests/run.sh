#!/usr/bin/env bash
set -eu

# run normal pytests, skip e2e tests
coverage run -m pytest -m "not e2e"

# clean out old coverage results
rm -rf ./tests/coverage

# regenerate coverate report
coverage html --directory ./tests/coverage
