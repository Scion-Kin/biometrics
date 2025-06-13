#!/usr/bin/env bash

cd ../ZKTeco
./puller.py --verbose
./main.py -m MilMall --verbose
./update_checker.sh
