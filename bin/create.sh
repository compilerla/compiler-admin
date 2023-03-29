#!/usr/bin/env bash
set -eu

SCRIPT_DIR=$(builtin cd "$(dirname ${BASH_SOURCE[0]})" && builtin pwd)

source "${SCRIPT_DIR}/common.sh"

__usage="
Usage: $(basename $0) USER [OPTIONS]

Arguments:
  USER         The account in $DOMAIN (sans domain) to create
  OPTIONS      A list of options for GAM user create, e.g.
    firstname User
    lastname Name
    recoveryemail something@something.com
    recoveryphone \"+1 (310) 555-5555\"

    See https://github.com/taers232c/GAMADV-XTD3/wiki/Users#create-a-user
    for the complete list of OPTIONS

    The user's password is randomly generated and requires reset on first login.
"

# print usage for -? or -h or --help
if [[ "$#" -lt 1 || "$1" =~ ^(-\?|-h|--help)$ ]]; then
    echo "$__usage"
    exit 0
fi

# the full account name to create
ACCOUNT="$1@$DOMAIN"
shift

# verify $ACCOUNT does not exist before continuing
if user_exists $ACCOUNT; then
    echo_ts "Account $ACCOUNT already exists, stopping"
    exit 1
else
    echo_ts "Account $ACCOUNT does not exist, continuing..."
fi

# Account creation

echo_ts "Creating account..."

gam create user $ACCOUNT password random changepassword "$@"

echo_ts "Adding to $TEAM group..."

gam user $ACCOUNT add groups member $TEAM

echo_ts "$ACCOUNT has been created"
