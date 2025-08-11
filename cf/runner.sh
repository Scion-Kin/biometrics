#!/usr/bin/env bash

source venv/bin/activate

cd ZKTeco
python3 main.py -m MilMall -b
python3 puller.py

cd ..
./cf/update_checker.sh
