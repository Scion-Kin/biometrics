#!/usr/bin/env bash

cd ../ZKTeco
./puller.py && ./main.py -m MilMall
./update_checker.sh
