#!/usr/bin/env bash
set -eu

SCRIPT_DIR=$(builtin cd "$(dirname ${BASH_SOURCE[0]})" && builtin pwd)

source "${SCRIPT_DIR}/common.sh"

__usage="
Usage: $(basename $0) USER

Arguments:
  USER         The account in $DOMAIN (sans domain) to sign out from all sessions
"

# print usage for -? or -h or --help
if [[ "$#" -lt 1 || "$1" =~ ^(-\?|-h|--help)$ ]]; then
    echo "$__usage"
    exit 0
fi

# the full account name to signout
ACCOUNT="$1@$DOMAIN"

# verify $ACCOUNT exists before continuing
if ! user_exists $ACCOUNT; then
    echo_ts "Account $ACCOUNT does not exist, stopping"
    exit 1
else
    echo_ts "Account $ACCOUNT exists, continuing..."
fi

echo_ts "Signing out $ACCOUNT from all active sessions..."

gam user $ACCOUNT signout
