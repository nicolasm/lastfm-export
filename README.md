# lastfm-export
### Export your Last.fm tracks and import them into a MySQL database

This script imports your Last.fm listening history inside a MySQL database.

The original script has been developed by [Matthew Lewis](http://mplewis.com/files/lastfm-scraper.html). It was coded to do a one-time import in a SQLite database.

Copyright (c) 2014-2015, Matthew Lewis

I have changed it in the following ways:                          
- MySQL with a normalised database                                
- import the missing tracks by comparing Last.fm number of tracks against the database
- getting rid of the "nowplaying" track if found
- reading user logins, passwords from .netrc
- insert the tracks in order of play

I provide a SQL script to create the database. The data model is made of:
- five tables
    - artist
    - album
    - track
    - play              ->  corresponds to the Last.fm track notion
    - various_artist    ->  album names are various artists albums, compilations...
- a insert_play stored procedure that:
    - finds the artist, album, track in the database or inserts them if not found.
    - inserts the play with the previous found or created elements.
- several views:
    - top artists/albums/tracks for the last 7, 30, 90, 365 days and all time.
    - view_plays
    - view_play_count_by_month
- a nb_days function used in the views.

Give execution rights to the Python script:
chmod u+x exportLastfm2Mysql.py

Call the Python script with your Last.fm username:
./exportLastfm2Mysql.py username

Copyright (c) 2015, Nicolas Meier
