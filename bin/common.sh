#!/usr/bin/env bash
set -eu

# Compiler's domain
DOMAIN="compiler.la"
# Compiler's archive account
ARCHIVE="archive@$DOMAIN"

# prints a simple timestamp HH:mm:ss
ts () {
    echo "$(date +%H:%m:%S)"
}

# prepend the timestamp to a message
echo_ts () {
    echo "[$(ts)] $1"
}

# checks if a user exists
# Return value 0 when user does exist, non-0 when user does not exist
user_exists () {
    gam info user "$1" quick &> /dev/null
}

# verify that the archive user exists
archive_user_exists() {
    if ! user_exists $ARCHIVE; then
        echo_ts "Compiler archive user $ARCHIVE not found! This is a problem!!"
        exit 1
    fi
}
