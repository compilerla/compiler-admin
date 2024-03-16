#!/usr/bin/env bash
set -eu

pre-commit install --install-hooks

echo -e "\nexport PATH=$PATH:/home/compiler/admin/.config/gyb" >> ~/.bashrc
