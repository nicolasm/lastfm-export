#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import sys

from lfmconf.lfmconf import get_lastfm_conf
from lfmdb import lfmdb
from stats.stats import process_track, retrieve_total_plays_from_db, \
    retrieve_total_json_tracks_from_db
from queries.inserts import get_query_insert_play

logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s %(levelname)s %(message)s'
)

conf = get_lastfm_conf()

nb_json_tracks_in_db = retrieve_total_json_tracks_from_db()
nb_plays_in_db = retrieve_total_plays_from_db()
nb_plays_to_insert = nb_json_tracks_in_db - nb_plays_in_db

query = """
select id, json from
(select id, json from json_track order by id desc limit %s) tmp
order by id
"""

if nb_plays_to_insert == 0:
    logging.info('Nothing new!')
    sys.exit(0)

new_plays = lfmdb.select(query % nb_plays_to_insert)

connection = lfmdb.create_connection()
cursor = connection.cursor()

parameters = []
for (track_id, json_track) in new_plays:
    logging.info('Track %s' % track_id)
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
        insert_query = get_query_insert_play()
        lfmdb.insert(connection,
                     cursor,
                     insert_query, (artist_name,
                                    transformed_track['artist_mbid'],
                                    album_name,
                                    transformed_track['album_mbid'],
                                    track_name,
                                    transformed_track['mbid'],
                                    transformed_track['url'],
                                    transformed_track['date_uts'],
                                    transformed_track['date_uts']
                                    ))
    except Exception as e:
        logging.exception(
            'An error occurred when inserting play into database!')
        logging.error(track_name, ', ', artist_name)
        sys.exit(1)

cursor.close()
connection.close()
