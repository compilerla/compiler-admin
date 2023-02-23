#!/usr/bin/env bash
set -eu

SCRIPT_DIR=$(builtin cd "$(dirname ${BASH_SOURCE[0]})" && builtin pwd)

source "${SCRIPT_DIR}/common.sh"

__usage="
Usage: $(basename $0) USER

Arguments:
  USER         The account in $DOMAIN (sans domain) with a local backup to archive
"

# print usage for -? or -h or --help
if [[ "$#" -lt 1 || "$1" =~ ^(-\?|-h|--help)$ ]]; then
    echo "$__usage"
    exit 0
fi

# quick sanity check
archive_user_exists

# the full account name to restore
ACCOUNT="$1@$DOMAIN"
# the name of the backup folder that should already exist
BACKUP="GYB-GMail-Backup-$ACCOUNT"

# verify $ACCOUNT exists before continuing
if $(ls $BACKUP &> /dev/null); then
    echo_ts "Found backup $BACKUP, starting the archive process..."
else
    echo_ts "Couldn't find a local backup $BACKUP, stopping"
    exit 1
fi

gyb --service-account --email $ARCHIVE --action restore --local-folder GYB-GMail-Backup-$ACCOUNT --label-restored $ACCOUNT

echo_ts "Email restore complete"
