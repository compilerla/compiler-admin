#!/usr/bin/env bash
set -e

read -p "Did you remember to check the project mapping? $TOGGL_PROJECT_INFO (Y/n): " check_project

if [[ "$check_project" ~= ^[^Yy]$ ]]; then
  echo "Check and then run this script again"
  exit 1
fi

CMD="time convert"
OPTS="--input $TOGGL_DATA --output $HARVEST_DATA"

exec compiler-admin $CMD $OPTS
