from lfmconf.lfmconf import get_lastfm_conf

QUERY_INSERT_INTO_JSON_TRACK = {
    'mysql': 'insert into json_track(json) values (%s)',
    'sqlite': 'insert into json_track(json) values (?)'}

QUERY_INSERT_INTO_PLAY = {
    'mysql': """
    insert into play(artist_name, artist_mbid,
                     album_name, album_mbid,
                     track_name, track_mbid, track_url,
                     play_date_uts, play_date)
    values (%s, %s, %s, %s, %s, %s, %s, %s, FROM_UNIXTIME(%s))
""",
    'sqlite': """
    insert into play(artist_name, artist_mbid,
                     album_name, album_mbid,
                     track_name, track_mbid, track_url,
                     play_date_uts, play_date)
    values (?, ?, ?, ?, ?, ?, ?, ?, datetime(?, 'unixepoch', 'localtime'))
"""}


conf = get_lastfm_conf()
dbms = conf['lastfm']['db']['dbms']


def get_query_insert_json_track():
    return QUERY_INSERT_INTO_JSON_TRACK[dbms]


def get_query_insert_play():
    return QUERY_INSERT_INTO_PLAY[dbms]
