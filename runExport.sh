#!/bin/bash -
cd ~/Code/github/lastfm-export/
if [ -r "./runConfig" ]; then
  . "./runConfig"
fi

./venv/bin/python export.py
if [[ $? = 0 ]]; then
    ./venv/bin/python import.py
fi
