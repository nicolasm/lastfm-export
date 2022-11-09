import collections
import math
import urllib

import requests

from queries.counts import get_query_count_json_tracks, get_query_count_plays
from lfmdb import lfmdb

api_url = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks' \
          '&user=%s&api_key=%s&format=json&page=%s&limit=%s'
track_api_url = 'https://ws.audioscrobbler.com/2.0/?method=track.getinfo' \
                '&api_key=%s&format=json&artist=%s&track=%s&autocorrect=1'


class LastfmStats(object):
    plays_per_page = 200

    def __init__(self, nb_pages_in_lastfm, nb_plays_in_lastfm,
                 nb_json_tracks_in_db):
        super(LastfmStats, self).__init__()
        self.nb_pages_in_lastfm = nb_pages_in_lastfm
        self.nb_plays_in_lastfm = nb_plays_in_lastfm
        self.nb_json_tracks_in_db = nb_json_tracks_in_db

    def nb_delta_pages(self):
        # Compute the number of pages to get to be up-to-date.
        return int(
            math.ceil(
                (float(self.nb_plays_in_lastfm) - float(
                    self.nb_json_tracks_in_db))
                / LastfmStats.plays_per_page))

    def nb_plays_for_first_page(self):
        return (self.nb_plays_in_lastfm - self.nb_json_tracks_in_db) \
               % LastfmStats.plays_per_page

    @staticmethod
    def get_lastfm_stats(user, api_key):
        # We need to get the first page so we can find out how many total pages
        # there are in our listening history.
        resp = recent_tracks(user, api_key, 1)
        total_pages = int(resp['recenttracks']['@attr']['totalPages'])
        total_plays_in_lastfm = int(resp['recenttracks']['@attr']['total'])

        total_plays_in_db = retrieve_total_json_tracks_from_db()

        return LastfmStats(total_pages, total_plays_in_lastfm,
                           total_plays_in_db)


def retrieve_total_json_tracks_from_db():
    """Get total json_tracks from the database."""
    return lfmdb.select_one(get_query_count_json_tracks())


def retrieve_total_plays_from_db():
    """Get total plays from the database."""
    return lfmdb.select_one(get_query_count_plays())


def recent_tracks(user, api_key, page):
    """Get the most recent tracks from `user` using `api_key`.
    Start at page `page` and limit results to `limit`."""
    return requests.get(
        api_url % (user, api_key, page, LastfmStats.plays_per_page)).json()


def track_info(api_key, artist, track):
    """Get track info using `api_key`."""
    r = requests.get(track_api_url % (api_key,
                                      urllib.parse.quote(
                                          artist.encode('utf8')),
                                      urllib.parse.quote(
                                          track.rstrip().encode('utf8'))))
    return r.json()


def flatten(d, parent_key=''):
    """From http://stackoverflow.com/a/6027615/254187.
    Modified to strip # symbols from dict keys."""
    items = []
    for k, v in d.items():
        new_key = parent_key + '_' + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            # Strip pound symbols from column names
            new_key = new_key.replace('#', '')
            items.append((new_key, v))
    return dict(items)


def process_track(track):
    """Removes `image` keys from track data.
    Replaces empty strings for values with None."""
    if 'image' in track:
        del track['image']
    flattened = flatten(track)
    for key, val in flattened.items():
        if val == '':
            flattened[key] = None
    return flattened
