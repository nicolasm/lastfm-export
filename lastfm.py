import math
import MySQLdb
import requests

api_url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json&page=%s&limit=%s'
track_api_url = 'http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=%s&format=json&artist=%s&track=%s&autocorrect=1'

class LastfmStats:
    plays_per_page = 200

    def __init__(self):
        self.nb_pages_in_lastfm = 0
        self.nb_pages_in_db = 0
        self.nb_plays_in_lastfm = 0
        self.nb_plays_in_db = 0

    def nb_delta_pages(self):
        return int(
            math.ceil(
                (float(self.nb_plays_in_lastfm) - float(self.nb_plays_in_db))
                / LastfmStats.plays_per_page));

    def nb_plays_for_first_page(self):
        return (self.nb_plays_in_lastfm - self.nb_plays_in_db)\
               % LastfmStats.plays_per_page

def recent_tracks(user, api_key, page, limit):
    """Get the most recent tracks from `user` using `api_key`. Start at page `page` and limit results to `limit`."""
    return requests.get(api_url % (user, api_key, page, limit)).json()
