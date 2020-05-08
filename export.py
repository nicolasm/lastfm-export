#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################
# This script imports your Last.fm listening history                  #
# inside a MySQL database.                                            #
#                                                                     #
# The original script has been developed by Matthew Lewis:            #
# http://mplewis.com/files/lastfm-scraper.html                        #
# It was coded to do a one-time import in a SQLite database.          #
# Copyright (c) 2014+2015, Matthew Lewis                              #
#                                                                     #
# I have changed it in the following ways:                            #
# - MySQL with a normalised database                                  #
# - import the missing tracks by comparing Last.fm number of tracks   #
#    against the database                                             #
# - getting rid of the "nowplaying" track if found                    #
# - reading user logins, passwords from .netrc                        #
# - insert the tracks in order of play                                #
#                                                                     #
# Copyright (c) 2015, Nicolas Meier                                   #
#######################################################################

import json
import sys

import MySQLdb

from lastfm.lastfm import LastfmStats, recent_tracks, \
    retrieve_total_json_tracks_from_db
from lastfmConf.lastfmConf import get_lastfm_conf

conf = get_lastfm_conf()

user = conf['lastfm']['service']['username']
api_key = conf['lastfm']['service']['api_key']

mysql = MySQLdb.connect(
    user=conf['lastfm']['db']['user'], passwd=conf['lastfm']['db']['password'],
    db=conf['lastfm']['db']['db_name'], charset='utf8')
mysql_cursor = mysql.cursor()

lastfm_stats = LastfmStats.get_lastfm_stats(mysql, user, api_key)
total_pages = lastfm_stats.nb_delta_pages()
total_plays_in_db = lastfm_stats.nb_json_tracks_in_db

print('Nb page to get: ', total_pages)

if total_pages == 0:
    print('Nothing to update!')
    sys.exit(1)

all_pages = []

for page_num in range(total_pages, 0, -1):
    print('Page', page_num, 'of', total_pages)
    page = recent_tracks(user, api_key, page_num)

    while page.get('recenttracks') is None:
        print('has no tracks. Retrying!')
        page = recent_tracks(user, api_key, page_num)

    all_pages.append(page)

# Iterate through all pages
num_pages = len(all_pages)
for page_num, page in enumerate(all_pages):
    print('Page', page_num + 1, 'of', num_pages)

    tracks = page['recenttracks']['track']

    # Remove the "nowplaying" track if found.
    if tracks[0].get('@attr'):
        if tracks[0]['@attr']['nowplaying'] == 'true':
            tracks.pop(0)

    # Get only the missing tracks.
    if page_num == 0:
        print('Fist page')
        print(lastfm_stats.nb_plays_in_lastfm)
        print(lastfm_stats.nb_json_tracks_in_db)
        nb_plays = lastfm_stats.nb_plays_for_first_page()
        tracks = tracks[0: nb_plays]
        print('Getting ', nb_plays)

    # On each page, iterate through all tracks
    num_tracks = len(tracks)

    json_tracks = []
    for track_num, track in enumerate(reversed(tracks)):
        print('Track', track_num + 1, 'of', num_tracks)
        json_tracks.append(json.dumps(track))

    try:
        query = 'insert into lastfm.json_track(json) values (%s)'
        mysql_cursor.executemany(query, json_tracks)
        mysql.commit()
    except mysql.Error as e:
            print(e)
            mysql.rollback()
            sys.exit(1)

print('Done!', retrieve_total_json_tracks_from_db(mysql), 'rows in table json_track.')
