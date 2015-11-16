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

Copyright (c) 2015, Nicolas Meier
