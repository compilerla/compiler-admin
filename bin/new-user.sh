#!/usr/bin/env bash
set -e

if [ $# -lt 3 ]; then
  echo "Usage: $0 <username> <First> <Last> [<notify>]"
  exit 1
fi

USERNAME=$1
FIRST=$2
LAST=$3
NOTIFY=${4:-}

CMD="user create"
OPTS="$USERNAME firstname $FIRST lastname $LAST"

if [[ "$NOTIFY" ]]; then
    OPTS="--notify $NOTIFY $OPTS"
fi

exec compiler-admin $CMD $OPTS
