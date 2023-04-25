#!/usr/bin/env bash
set -u

SCRIPT_DIR=$(builtin cd "$(dirname ${BASH_SOURCE[0]})" && builtin pwd)

source "${SCRIPT_DIR}/common.sh"

__usage="
Usage: $(basename $0) USER TYPE

Arguments:
  USER         The account in $DOMAIN (sans domain) to assign
  CLIENT       The client code used to construct the group
"

# print usage for -? or -h or --help
if [[ "$#" -lt 2 || "$1" =~ ^(-\?|-h|--help)$ ]]; then
    echo "$__usage"
    exit 0
fi

# the full account name to assign
ACCOUNT="$1@$DOMAIN"
# the full group name to assign
GROUP="$2@$DOMAIN"

# verify $ACCOUNT exists before continuing
if ! user_exists $ACCOUNT; then
    echo_ts "Account $ACCOUNT does not exist, stopping"
    exit 1
else
    echo_ts "Account $ACCOUNT exists, continuing..."
fi

# add to client group
gam user $ACCOUNT add groups member $GROUP

echo_ts "Account updated"
