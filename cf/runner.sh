#!/usr/bin/env bash

cd ../ZKTeco
./puller.py && ./main.py -m MilMall

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
