#!/bin/bash -
cd ~/Code/GitHub/lastfm-export/
./exportLastfm2Mysql.py $1
if [[ $? = 0 ]]; then
    ../lastfm-notebooks/runPlays.sh
fi
