QUERY_COUNT_JSON_TRACKS = 'select count(*) from json_track'

QUERY_COUNT_PLAYS = 'select count(*) from play'


def get_query_count_json_tracks():
    return QUERY_COUNT_JSON_TRACKS


def get_query_count_plays():
    return QUERY_COUNT_PLAYS
