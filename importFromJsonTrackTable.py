#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import netrcfile
import MySQLdb
import json
import sys

# Get the MySQL connection data.
from lastfm.lastfm import process_track, check_track_in_db, track_info

login = netrcfile.retrieve_from_netrc('lastfm.mysql')

mysql = MySQLdb.connect(
    user=login[0], passwd=login[2], db=login[1], charset='utf8')
mysql_cursor = mysql.cursor()

# Get the Last.fm API key
login = netrcfile.retrieve_from_netrc('lastfm')
api_key = login[2]

mysql_cursor.execute('select id, json from lastfm.json_track order by id')

parameters = []
for (id, json_track) in mysql_cursor:
    print('Track', id)
    track = json.loads(json_track)

    transformed_track = process_track(track)
    artist_name = transformed_track['artist_text']
    album_name = transformed_track['album_text']
    track_name = transformed_track['name']

    # Cut artist name if too long.
    if len(artist_name) > 512:
        artist_name = artist_name[:512]

    # Cut track name if too long.
    if len(track_name) > 512:
        track_name = track_name[:512]

    parameters.append((track_name,
                       transformed_track['mbid'],
                       transformed_track['url'],
                       transformed_track['date_uts'],
                       artist_name,
                       transformed_track['artist_mbid'],
                       album_name,
                       transformed_track['album_mbid']))

    # if len(parameters) % 200 == 0:
    #     mysql_cursor.executemany("call insert_play(%s, %s, %s, %s, %s, %s, %s, %s)", parameters)
    #     parameters.clear()

    try:
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
    except mysql.Error as e:
        print(e)
        print(track_name, ', ', artist_name)
        mysql.rollback()
        sys.exit(1)

# mysql_cursor.executemany("call insert_play(%s, %s, %s, %s, %s, %s, %s, %s)", parameters)
# parameters.clear()

mysql_cursor.close()
