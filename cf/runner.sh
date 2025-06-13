#!/usr/bin/env bash

source venv/bin/activate

cd ZKTeco
python3 puller.py --verbose
python3 main.py -m MilMall --verbose

cd ..
./cf/update_checker.sh
