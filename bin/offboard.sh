#!/usr/bin/env bash
set -eu

SCRIPT_DIR=$(builtin cd "$(dirname ${BASH_SOURCE[0]})" && builtin pwd)

source "${SCRIPT_DIR}/common.sh"

__usage="
Usage: $(basename $0) USER [ALIAS]

Arguments:
  USER         The account in $DOMAIN (sans domain) to offboard
  ALIAS        Optional: an account in $DOMAIN (sans domain) that will get an alias added for the offboarded user
"

# print usage for -? or -h or --help
if [[ "$#" -lt 1 || "$1" =~ ^(-\?|-h|--help)$ ]]; then
    echo "$__usage"
    exit 0
fi

# quick sanity check
archive_user_exists

# the full account name to offboard
ACCOUNT="$1@$DOMAIN"

# verify $ACCOUNT exists before continuing
if user_exists $ACCOUNT; then
    echo_ts "Account $ACCOUNT exists, starting the offboard process..."
else
    echo_ts "Account $ACCOUNT does not exist, stopping"
    exit 1
fi

# check for the optional ALIAS target
if [[ "$#" -gt 1 ]]; then
    ALIAS="$2@compiler.la"
    if user_exists $ALIAS; then
        echo_ts "Alias target $ALIAS exists, $ACCOUNT will be added as an alias"
    else
        echo_ts "Alias target does not exist, stopping"
        exit 1
    fi
else
    ALIAS=""
fi

# Offboard process

echo_ts "Suspending account..."

gam suspend user $ACCOUNT noactionifalias

echo_ts "Suspending account done"

echo_ts "Removing from groups..."

gam user $ACCOUNT delete groups

echo_ts "Removed from groups"

echo_ts "Backing up email..."

gyb --service-account --email $ACCOUNT --action backup

echo_ts "Email backup complete"

echo_ts "Restoring email to $ARCHIVE..."

gyb --service-account --email $ARCHIVE --action restore --local-folder GYB-GMail-Backup-$ACCOUNT --label-restored $ACCOUNT

echo_ts "Starting Drive and Calendar transfer..."

gam create transfer $ACCOUNT calendar,drive $ARCHIVE all releaseresources

STATUS=""
until [[ "$STATUS" =~ "Overall Transfer Status: completed" ]]
do
    echo_ts "Transfer in progress..."
    STATUS=$(gam show transfers olduser $ACCOUNT)
    sleep 3
done

echo_ts "Drive and Calendar transfer complete"

echo_ts "Starting account deletion..."

gam delete user $ACCOUNT noactionifalias

echo_ts "Account deletion complete"

if [[ "$ALIAS" != "" ]]; then
    echo_ts "Adding an alias on account $ALIAS..."
    gam create alias $ACCOUNT user $ALIAS
    echo_ts "Alias added"
fi

echo_ts "Offboard of $ACCOUNT complete"
