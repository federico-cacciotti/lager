#!/bin/bash
set -e

source /home/polocalc/lager_venv/bin/activate
cd /home/polocalc/lager

while true; do
    exec python3 follow_POI.py --config config/follow_POI_config.yaml
    EXIT_CODE=$?
    sleep 5
done