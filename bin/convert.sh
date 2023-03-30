#!/usr/bin/env bash
set -u

SCRIPT_DIR=$(builtin cd "$(dirname ${BASH_SOURCE[0]})" && builtin pwd)

source "${SCRIPT_DIR}/common.sh"

__usage="
Usage: $(basename $0) USER TYPE

Arguments:
  USER         The account in $DOMAIN (sans domain) to convert
  TYPE         The type of conversion [STAFF or PARTNER]
"

# print usage for -? or -h or --help
if [[ "$#" -lt 2 || "$1" =~ ^(-\?|-h|--help)$ ]]; then
    echo "$__usage"
    exit 0
fi

# the full account name to convert
ACCOUNT="$1@$DOMAIN"

# verify $ACCOUNT exists before continuing
if ! user_exists $ACCOUNT; then
    echo_ts "Account $ACCOUNT does not exist, stopping"
    exit 1
else
    echo_ts "Account $ACCOUNT exists, continuing..."
fi

TYPE="$2"

if echo "$TYPE" | grep -i staff &> /dev/null; then
    if user_is_staff "$ACCOUNT"; then
        echo_ts "Account $ACCOUNT is already a member of $STAFF"
        exit 1
    fi
    GROUP="$STAFF"
elif echo "$TYPE" | grep -i partner &> /dev/null; then
    if user_is_partner "$ACCOUNT"; then
        echo_ts "Account $ACCOUNT is already a member of $PARTNERS"
        exit 1
    fi
    GROUP="$PARTNERS"
else
    echo_ts "Unsupported conversion type: $TYPE"
    exit 1
fi

echo_ts "Converting $ACCOUNT to $TYPE..."

gam user $ACCOUNT add groups member $GROUP
