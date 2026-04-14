#!/usr/bin/env bash
set -eu

pre-commit install --install-hooks

# configures shell completion for bash `compiler-admin`
# https://click.palletsprojects.com/en/stable/shell-completion/
_COMPILER_ADMIN_COMPLETE=bash_source compiler-admin > ./compiler-admin-complete.bash
echo "source ./compiler-admin-complete.bash" >> ~/.bashrc
