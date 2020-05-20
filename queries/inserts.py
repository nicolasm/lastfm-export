from lfmconf.lfmconf import get_lastfm_conf

query_insert_into_json_track = {
    'mysql': 'insert into json_track(json) values (%s)',
    'sqlite': 'insert into json_track(json) values (?)'}

query_insert_into_play = {
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
    return query_insert_into_json_track[dbms]


def get_query_insert_play():
    return query_insert_into_play[dbms]
