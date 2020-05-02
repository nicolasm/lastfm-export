#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

import MySQLdb

import netrcfile
from lastfm.lastfm import process_track, retrieve_total_plays_from_db, \
    retrieve_total_json_tracks_from_db

login = netrcfile.retrieve_from_netrc('lastfm.mysql')

mysql = MySQLdb.connect(
    user=login[0], passwd=login[2], db=login[1], charset='utf8')
mysql_cursor = mysql.cursor()

login = netrcfile.retrieve_from_netrc('lastfm')
api_key = login[2]

nb_json_tracks_in_db = retrieve_total_json_tracks_from_db(mysql)
nb_plays_in_db = retrieve_total_plays_from_db(mysql)
nb_plays_to_insert = nb_json_tracks_in_db - nb_plays_in_db

query = """
select id, json from
(select id, json from json_track order by id desc limit %s) tmp
order by id
"""

mysql_cursor.execute(query % nb_plays_to_insert)

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

    try:
        insert_query = 'insert into play(artist_name, artist_mbid,' \
                       'album_name, album_mbid,' \
                       'track_name, track_mbid, track_url,' \
                       'play_date_uts, play_date) ' \
                       'values ' \
                       '(%s, %s, %s, %s, %s, %s, %s, %s, FROM_UNIXTIME(play_date_uts))'
        mysql_cursor.execute(insert_query,
                             (artist_name,
                              transformed_track['artist_mbid'],
                              album_name,
                              transformed_track['album_mbid'],
                              track_name,
                              transformed_track['mbid'],
                              transformed_track['url'],
                              transformed_track['date_uts']
                              ))
        mysql.commit()
    except mysql.Error as e:
        print(e)
        print(track_name, ', ', artist_name)
        mysql.rollback()
        sys.exit(1)

mysql_cursor.close()
