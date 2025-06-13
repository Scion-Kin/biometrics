#!/usr/bin/env bash
# This script checks for updates from the GitHub repository and updates the local copy if necessary.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

res=$(git pull 2>&1)
status=$?

if [[ $status -ne 0 ]]; then
    echo "Git pull failed:"
    echo "$res"
    exit 1
fi

if echo "$res" | grep -qE "Already up[ -]to[ -]date"; then
    echo "No updates available."
else
    echo "Updates applied successfully:"
    echo "$res"
    echo "Running post-update patch..."
    python3 "$SCRIPT_DIR/patches.py"
fi
