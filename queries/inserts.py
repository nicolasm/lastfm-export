query_insert_into_json_track = 'insert into json_track(json) values (?)'

query_insert_into_play = """
    insert into play(artist_name, artist_mbid,
                     album_name, album_mbid,
                     track_name, track_mbid, track_url,
                     play_date_uts, play_date)
    values (?, ?, ?, ?, ?, ?, ?, ?, datetime(?, 'unixepoch', 'localtime'))
"""


def get_query_insert_json_track():
    return query_insert_into_json_track


def get_query_insert_play():
    return query_insert_into_play
