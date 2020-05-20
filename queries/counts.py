query_count_json_tracks = 'select count(*) from json_track'

query_count_plays = 'select count(*) from play'


def get_query_count_json_tracks():
    return query_count_json_tracks


def get_query_count_plays():
    return query_count_plays
