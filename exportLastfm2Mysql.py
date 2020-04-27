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

import sys
import requests
import collections
import math
import netrcfile
import MySQLdb
import re
import urllib
import json

import lastfm
from lastfm.lastfm import LastfmStats, recent_tracks

if len(sys.argv) != 2:
    raise netrcfile.NetrcParseError('Missing Last.fm username.')

# Call the script with your Last.fm username.
user = sys.argv[1]

# Get the Last.fm API key
login = netrcfile.retrieve_from_netrc('lastfm')
api_key = login[2]

# These are the API parameters for our scraping requests.
per_page = 200
api_url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json&page=%s&limit=%s'
track_api_url = 'http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=%s&format=json&artist=%s&track=%s&autocorrect=1'


def flatten(d, parent_key=''):
    """From http://stackoverflow.com/a/6027615/254187. Modified to strip # symbols from dict keys."""
    items = []
    for k, v in d.items():
        new_key = parent_key + '_' + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            # Strip pound symbols from column names
            new_key = new_key.replace('#', '')
            items.append((new_key, v))
    return dict(items)


def process_track(track):
    """Removes `image` keys from track data. Replaces empty strings for values with None."""
    if 'image' in track:
        del track['image']
    flattened = flatten(track)
    for key, val in flattened.items():
        if val == '':
            flattened[key] = None
    return flattened


def check_track_in_db(track_name, artist_name, album_name):
    cursor = mysql.cursor()
    cursor.execute("select check_track_in_db(%s, %s, %s)",
                   (track_name, artist_name, album_name))
    return cursor.fetchone()[0]


# We need to get the first page so we can find out how many total pages there are in our listening history.
""" resp = lastfm.recent_tracks(user, api_key, 1, 200)
total_pages = int(resp['recenttracks']['@attr']['totalPages'])
total_plays_in_lastfm = int(resp['recenttracks']['@attr']['total']) """

# Get the MySQL connection data.
login = netrcfile.retrieve_from_netrc('lastfm.mysql')

mysql = MySQLdb.connect(
    user=login[0], passwd=login[2], db=login[1], charset='utf8')
mysql_cursor = mysql.cursor()

lastfm_stats = LastfmStats.get_lastfm_stats(mysql, user, api_key)
total_pages = lastfm_stats.nb_delta_pages()
total_plays_in_db = lastfm_stats.nb_plays_in_db

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
        print(lastfm_stats.nb_plays_in_db)
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

    """ for track_num, track in enumerate(reversed(tracks)):
        print('Track', track_num + 1, 'of', num_tracks)

        transformed_track = process_track(track)

        artist_name = transformed_track['artist_text']
        album_name = transformed_track['album_text']
        track_name = transformed_track['name']

        if not check_track_in_db(track_name, artist_name, album_name):
            info = lastfm.track_info(api_key, artist_name, track_name)
            info = process_track(info)

        # Cut artist name if too long.
        if len(artist_name) > 512:
            artist_name = artist_name[:512]

        # Cut track name if too long.
        if len(track_name) > 512:
            track_name = track_name[:512]

        # Call procedure to insert current play and track, artist, album if needed.
        try:
            mysql_cursor.execute('insert into json_track(json) values (%s)', [
                                 json.dumps(track)])
            mysql_cursor.callproc("insert_play",
                        (track_name,
                         transformed_track['mbid'],
                         transformed_track['url'],
                         transformed_track['date_uts'],
                         artist_name,
                         transformed_track['artist_mbid'],
                         album_name,
                         transformed_track['album_mbid']))
            mysql.commit()
        except mysql.connector.Error as e:
            print(e)
            print(track_name, ', ', artist_name)
            print(info)
            mysql.rollback()
            sys.exit(1) """

# Display number of plays in database.
print('Done!', lastfm.retrieve_total_plays_from_db(mysql), 'rows in table `play.')
