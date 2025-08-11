#!/bin/bash

# Check arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <start_date: YYYY-MM-DD> <end_date: YYYY-MM-DD>"
    exit 1
fi

start_date="$1"
end_date="$2"

# Validate dates
if ! date -d "$start_date" >/dev/null 2>&1; then
    echo "Invalid start date format. Use YYYY-MM-DD."
    exit 1
fi

if ! date -d "$end_date" >/dev/null 2>&1; then
    echo "Invalid end date format. Use YYYY-MM-DD."
    exit 1
fi

current_date="$start_date"

# Loop including the end date
while [[ "$current_date" < "$end_date" ]] || [[ "$current_date" == "$end_date" ]]; do
    next_date=$(date -I -d "$current_date + 1 day")

    python3 main.py --verbose -m MilMall --import "$current_date" "$next_date" -b

    # Break if we reached the end date
    if [[ "$current_date" == "$end_date" ]]; then
        break
    fi

    sleep 30
    current_date="$next_date"
done
