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

def recent_tracks(user, api_key, page, limit):
    """Get the most recent tracks from `user` using `api_key`. Start at page `page` and limit results to `limit`."""
    return requests.get(api_url % (user, api_key, page, limit)).json()

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
    print 'Nothing to update!'
    sys.exit(1)

all_pages = []
for page_num in xrange(total_pages, 0, -1):
    print 'Page', page_num, 'of', total_pages
    page = recent_tracks(user, api_key, page_num, 200)
    all_pages.append(page)

# Iterate through all pages
num_pages = len(all_pages)
for page_num, page in enumerate(all_pages):
    print 'Page', page_num + 1, 'of', num_pages
 
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

        # Cut artist name if too long.
        if len(transformed_track['artist_text']) > 512:
            transformed_track['artist_text'] = transformed_track['artist_text'][:512]
        
        # Cut track name if too long.
        if len(transformed_track['name']) > 512:
            transformed_track['name'] = transformed_track['name'][:512]

        # Call procedure to insert current play and track, artist, album if needed.
        mysql_cursor.callproc("insert_play",
        (transformed_track['name'], transformed_track['mbid'], transformed_track['url'], transformed_track['date_uts'],
        transformed_track['artist_text'], transformed_track['artist_mbid'], transformed_track['album_text'], transformed_track['album_mbid']))

# Display number of plays in database.
print 'Done!', retrieve_total_plays_from_db(), 'rows in table `play.'
