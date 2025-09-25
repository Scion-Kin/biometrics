#!/usr/bin/env bash

source venv/bin/activate
./cf/update_checker.sh

cd ZKTeco
source ./att_process.ring

# Check if last process was more than 20 minutes ago
if [ -z "$LAST" ]; then
    LAST=$(date -Iseconds) # If LAST is not set, initialize it to current time
fi

last_process=$(date -d "$LAST" +%s)
now=$(date +%s)
python3 puller.py

if (( (now - last_process) > 1200 )); then
    echo "Last process was more than 20 minutes ago. Importing missed data..."
    sudo service cron stop

    # convert last_process to YYYY-MM-DD format
    last_process=$(date -I -d "@$last_process")
    tomorrow=$(date -I -d "tomorrow")
    ./importer.sh "$last_process" "$tomorrow"

    sudo service cron start
else
    echo "Last process was within the last 20 minutes. No missed data to import."
    python3 main.py -m MilMall -b
fi 

printf "LAST=%s\n" "$(date -Iseconds)" > att_process.ring
