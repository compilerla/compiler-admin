#!/usr/bin/env bash
set -eu

__usage="
Usage: $(basename $0) USER [ALIAS]

Arguments:
  USER         The account in compiler.la (sans domain) to offboard
  ALIAS        Optional: an account in compiler.la (sans domain) that will get an alias added for the offboarded user
"

# function prints a simple timestamp HH:mm:ss
ts () {
    echo "$(date +%H:%m:%S)"
}

# function checks if a user exists
# Return value 0 when user does exist, non-0 when user does not exist
check_user () {
    gam info user "$1" quick &> /dev/null
}

# print usage for -? or -h or --help
if [[ "$#" -lt 1 || "$1" =~ ^(-\?|-h|--help)$ ]]; then
    echo "$__usage"
    exit 0
fi

# Compiler's archive account
ARCHIVE="archive@compiler.la"
# the USER to offboard
USER=$1
# the full account name
ACCOUNT="$USER@compiler.la"

# quick sanity check
if ! check_user $ARCHIVE; then
    echo "[$(ts)] Compiler archive user $ARCHIVE does not exist!! This is a problem!"
    exit 1
fi

# verify $ACCOUNT exists before continuing
if check_user $ACCOUNT; then
    echo "[$(ts)] Account $ACCOUNT exists, starting the offboard process..."
else
    echo "[$(ts)] Account $ACCOUNT does not exist, stopping"
    exit 1
fi

# check for the optional ALIAS target
if [[ "$#" -gt 1 ]]; then
    ALIAS="$2@compiler.la"
    if check_user $ALIAS; then
        echo "[$(ts)] Alias target $ALIAS exists, $ACCOUNT will be added as an alias"
    else
        echo "[$(ts)] Alias target does not exist, stopping"
        exit 1
    fi
else
    ALIAS=""
fi

# Offboard process

echo "[$(ts)] Suspending account..."

gam suspend user $ACCOUNT noactionifalias

echo "[$(ts)] Suspending account done"

echo "[$(ts)] Removing from groups..."

gam user $ACCOUNT delete groups

echo "[$(ts)] Removed from groups"

echo "[$(ts)] Backing up email..."

gyb --service-account --email $ACCOUNT --action backup

echo "[$(ts)] Email backup complete"

echo "[$(ts)] Restoring email to $ARCHIVE..."

gyb --service-account --email $ARCHIVE --action restore --local-folder GYB-GMail-Backup-$ACCOUNT --label-restored $ACCOUNT

echo "[$(ts)] Email restore complete"

echo "[$(ts)] Starting Drive and Calendar transfer..."

gam create transfer $ACCOUNT calendar,drive $ARCHIVE all releaseresources

STATUS=""
until [[ "$STATUS" =~ "Overall Transfer Status: completed" ]]
do
    echo "[$(ts)] Transfer in progress..."
    STATUS=$(gam show transfers olduser $ACCOUNT)
    sleep 3
done

echo "[$(ts)] Drive and Calendar transfer complete"

echo "[$(ts)] Starting account deletion..."

gam delete user $ACCOUNT noactionifalias

echo "[$(ts)] Account deletion complete"

if [[ "$ALIAS" != "" ]]; then
    echo "[$(ts)] Adding an alias on account $ALIAS..."
    gam create alias $ACCOUNT user $ALIAS
    echo "[$(ts)] Alias added"
fi

echo "[$(ts)] Offboard of $ACCOUNT complete"
