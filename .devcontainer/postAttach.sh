#!/usr/bin/env bash
set -eu

pre-commit install --install-hooks

echo -e "\nexport PATH=$PATH:/home/$USER/.config/compiler-admin/gyb" >> ~/.bashrc
