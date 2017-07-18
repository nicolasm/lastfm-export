#!/usr/bin/env python2
#-*- coding: utf-8 -*-

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
import netrc
import MySQLdb
import re
import urllib
import string
import zc.lockfile

lock = zc.lockfile.LockFile('lock')

reload(sys)
sys.setdefaultencoding('utf8')

if len(sys.argv) != 2:
    raise netrc.NetrcParseError('Missing Last.fm username.')

# Call the script with your Last.fm username.
user = sys.argv[1]

def retrieve_from_netrc(machine):
    login = netrc.netrc().authenticators(machine)
    if not login:
        raise netrc.NetrcParseError('No authenticators for %s' % machine)
    return login

# Get the Last.fm API key
login = retrieve_from_netrc('lastfm')
api_key = login[2]

# These are the API parameters for our scraping requests.
per_page = 200
api_url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json&page=%s&limit=%s'
track_api_url = 'http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=%s&format=json&artist=%s&track=%s&autocorrect=1'

printable = set(string.printable)

def recent_tracks(user, api_key, page, limit):
    """Get the most recent tracks from `user` using `api_key`. Start at page `page` and limit results to `limit`."""
    return requests.get(api_url % (user, api_key, page, limit)).json()

def track_info(api_key, artist, track):
    """Get track info using `api_key`."""
    r = requests.get(track_api_url % (api_key,
                                      urllib.quote(artist.encode('utf8')),
                                      urllib.quote(track.rstrip().encode('utf8'))))
    return r.json()

def flatten(d, parent_key=''):
    """From http://stackoverflow.com/a/6027615/254187. Modified to strip # symbols from dict keys."""
    items = []
    for k, v in d.items():
        new_key = parent_key + '_' + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            new_key = new_key.replace('#', '')  # Strip pound symbols from column names
            items.append((new_key, v))
    return dict(items)

def process_track(track):
    """Removes `image` keys from track data. Replaces empty strings for values with None."""
    if 'image' in track:
        del track['image']
    flattened = flatten(track)
    for key, val in flattened.iteritems():
        if val == '':
            flattened[key] = None
    return flattened

def retrieve_total_plays_from_db():
    """Get total plays from the database."""
    mysql.query('select count(*) from play')
    result = mysql.use_result()
    total_tracks_db = result.fetch_row()[0][0]
    return total_tracks_db

def check_track_in_db(track_name, artist_name, album_name):
    cursor = mysql.cursor()
    cursor.execute("select check_track_in_db(%s, %s, %s)", (track_name, artist_name, album_name))
    return cursor.fetchone()[0]

# We need to get the first page so we can find out how many total pages there are in our listening history.
resp = recent_tracks(user, api_key, 1, 200)
total_pages = int(resp['recenttracks']['@attr']['totalPages'])
total_plays_in_lastfm = int(resp['recenttracks']['@attr']['total'])

# Get the MySQL connection data.
login = retrieve_from_netrc('lastfm.mysql')

mysql = MySQLdb.connect(user=login[0],passwd=login[2],db=login[1], charset='utf8')
mysql_cursor = mysql.cursor()

total_plays_in_db = retrieve_total_plays_from_db()

# Compute the number of pages to get to be up-to-date.
total_pages = int(math.ceil((float(total_plays_in_lastfm) - float(total_plays_in_db)) / per_page));

if total_pages == 0:
    print('Nothing to update!')
    lock.close()
    sys.exit(1)

all_pages = []
for page_num in xrange(total_pages, 0, -1):
    print('Page', page_num, 'of', total_pages)
    page = recent_tracks(user, api_key, page_num, 200)
    all_pages.append(page)

# Iterate through all pages
num_pages = len(all_pages)
for page_num, page in enumerate(all_pages):
    print('Page', page_num + 1, 'of', num_pages)
 
    tracks = page['recenttracks']['track']
    
    ## Remove the "nowplaying" track if found.
    if tracks[0].get('@attr'):
        if tracks[0]['@attr']['nowplaying'] == 'true':
            tracks.pop(0)

    ## Get only the missing tracks.
    if page_num == 0:
        tracks = tracks[0: (total_plays_in_lastfm - total_plays_in_db) % per_page]

    # On each page, iterate through all tracks
    for track in reversed(tracks):
        # Process each track and insert it into the `tracks` table
        transformed_track = process_track(track)

        artist_name = transformed_track['artist_text']
        album_name = transformed_track['album_text']
        track_name = transformed_track['name']
        track_duration = '0'

        if not check_track_in_db(track_name, artist_name, album_name):
            info = track_info(api_key, artist_name, track_name)
            info = process_track(info)

            if (not (info.get("track_duration")) or (info["track_duration"] == "0")):
                m = re.match('(.*)(?:(?:-\s*|\(\s*|\s)(?:F|f)(?:t|eat|eaturing)(?:\.|\s).*)', track_name)
                if m:
                    name_without_featuring = m.group(1)
                    name_without_featuring = \
                        name_without_featuring[:-1] if ((name_without_featuring[-1:] == '-')
                                                        or(name_without_featuring[-1:] == '('))\
                                                    else name_without_featuring
                    try:
                        if not check_track_in_db(name_without_featuring, artist_name, album_name):
                            info = track_info(api_key, artist_name, name_without_featuring)
                            info = process_track(info)
                    except:
                        print(track_name, ', ', artist_name, ', ', album_name)
                        print(info)
            else:
                print("Track already in db", track_name, ', ', artist_name, ', ', album_name)

            if (not (info.get("track_duration")) or (info["track_duration"] == "0")):
                m = re.match('(.*)\s*\(.*\)', track_name)
                if m:
                    name_without_comment = m.group(1)
                    if not check_track_in_db(name_without_comment, artist_name, album_name):
                        info = track_info(api_key, artist_name, name_without_comment)
                        info = process_track(info)
            else:
                print("Track already in db", track_name, ', ', artist_name, ', ', album_name)

            if (info.get("track_duration")):
                track_duration = info["track_duration"]
            else:
                track_duration = '0'
        else:
            print("Track already in db", track_name, ', ', artist_name, ', ', album_name)

            # Cut artist name if too long.
        if len(artist_name) > 512:
            artist_name = artist_name[:512]
        
        # Cut track name if too long.
        if len(track_name) > 512:
            track_name = track_name[:512]

        # Call procedure to insert current play and track, artist, album if needed.
        try:
            mysql_cursor.callproc("insert_play",
                        (track_name,
                         int(track_duration) / 1000,
                         transformed_track['mbid'],
                         transformed_track['url'],
                         transformed_track['date_uts'],
                         artist_name,
                         transformed_track['artist_mbid'],
                         album_name,
                         transformed_track['album_mbid']))
        except:
            print int(track_duration)
            print(track_name, ', ', artist_name)
            print(info)

# Display number of plays in database.
print('Done!', retrieve_total_plays_from_db(), 'rows in table `play.')

lock.close()
