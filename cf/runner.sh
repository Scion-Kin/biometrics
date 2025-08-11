#!/usr/bin/env bash

source venv/bin/activate
./cf/update_checker.sh

cd ZKTeco
python3 main.py -m MilMall -b
python3 puller.py
