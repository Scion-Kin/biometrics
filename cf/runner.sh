#!/usr/bin/env bash

source venv/bin/activate

cd ZKTeco
python3 puller.py
python3 main.py -m MilMall

cd ..
./cf/update_checker.sh
