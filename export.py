#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################
# This script imports your Last.fm listening history                  #
# inside a MySQL or Sqlite database.                                  #
#                                                                     #
# Copyright (c) 2015-2020, Nicolas Meier                              #
#######################################################################

import json
import logging
import sys

from lfmconf.lfmconf import get_lastfm_conf
from lfmdb import lfmdb
from stats.stats import LastfmStats, recent_tracks, \
    retrieve_total_json_tracks_from_db
from queries.inserts import get_query_insert_json_track

logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s %(levelname)s %(message)s'
)

conf = get_lastfm_conf()

user = conf['lastfm']['service']['username']
api_key = conf['lastfm']['service']['apiKey']

lastfm_stats = LastfmStats.get_lastfm_stats(user, api_key)
total_pages = lastfm_stats.nb_delta_pages()
total_plays_in_db = lastfm_stats.nb_json_tracks_in_db

logging.info('Nb page to get: %d' % total_pages)

if total_pages == 0:
    logging.info('Nothing to update!')
    sys.exit(1)

all_pages = []

for page_num in range(total_pages, 0, -1):
    logging.info('Page %d of %d' % (page_num, total_pages))
    page = recent_tracks(user, api_key, page_num)

    while page.get('recenttracks') is None:
        logging.info('has no tracks. Retrying!')
        page = recent_tracks(user, api_key, page_num)

    all_pages.append(page)

# Iterate through all pages
num_pages = len(all_pages)
for page_num, page in enumerate(all_pages):
    logging.info('Page %d of %d' % (page_num + 1, num_pages))

    tracks = page['recenttracks']['track']

    # Remove the "nowplaying" track if found.
    if tracks[0].get('@attr'):
        if tracks[0]['@attr']['nowplaying'] == 'true':
            tracks.pop(0)

    # Get only the missing tracks.
    if page_num == 0:
        logging.info('Fist page')
        nb_plays = lastfm_stats.nb_plays_for_first_page()
        tracks = tracks[0: nb_plays]
        logging.info('Getting %d plays' % nb_plays)

    # On each page, iterate through all tracks
    num_tracks = len(tracks)

    json_tracks = []
    for track_num, track in enumerate(reversed(tracks)):
        logging.info('Track %d of %d' % (track_num + 1, num_tracks))
        json_tracks.append(json.dumps(track))

    try:
        lfmdb.insert_many(get_query_insert_json_track(), json_tracks)
    except Exception:
        sys.exit(1)

logging.info(
    'Done! %d rows in table json_track.' % retrieve_total_json_tracks_from_db())
