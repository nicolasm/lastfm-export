#!/bin/bash -
cd ~/Code/GitHub/lastfm-export/
./venv/bin/python export.py
if [[ $? = 0 ]]; then
    ./venv/bin/python import.py
fi
