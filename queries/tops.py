from lfmconf.lfmconf import get_lastfm_conf

query_play_count_by_month = """
    select * from view_play_count_by_month v
    where substr(v.yr_month, 1, 4) =
"""

query_top_with_remaining = """
    with top as (
        {query_top}
    ),
    total_count as (
        {query_play_count}
    )

    select t.*
    from top t
"""

query_top_artists_with_remaining = query_top_with_remaining + \
"""
    union all
    select 'Remaining artists' as artist_name,
    ((select tc.play_count from total_count tc)
    -
    (select sum(play_count) from top)) as play_count
"""

query_top_albums_with_remaining = query_top_with_remaining + \
"""
    union all
    select 'Remaining albums' as album_name,
    '...' as artist_name,
    ((select tc.play_count from total_count tc)
    -
    (select sum(play_count) from top)) as play_count
"""
query_top_tracks_with_remaining = query_top_with_remaining + \
"""
    union all
    select 'Remaining tracks' as track_name,
    '...' as artist_name,
    '...' as album_name,
    ((select tc.play_count from total_count tc)
    -
    (select sum(play_count) from top)) as play_count
"""

query_top_artists = """
    select p.artist_name,
           count(p.id) as play_count
    from play p
    where p.artist_name not like 'VA %'
    {condition}
    group by p.artist_name
    order by count(p.id) desc
"""

query_top_albums = """
    select p.album_name,
           p.artist_name,
           count(p.id) as play_count
    from play p
    where 1 = 1
    {condition}
    group by p.album_name, p.artist_name
    order by count(p.id) desc
"""

query_top_tracks = """
    select p.track_name,
           p.artist_name,
           p.album_name,
           count(p.id) as play_count
    from play p
    where 1 = 1
    {condition}
    group by p.track_name, p.artist_name, p.album_name
    order by count(p.id) desc
"""

query_play_count = """
    select count(p.id) as play_count
    from play p
    where 1 = 1
    {condition}
"""

conf = get_lastfm_conf()
dbms = conf['lastfm']['db']['dbms']


def build_query_play_count_by_month():
    if dbms == 'mysql':
        return query_play_count_by_month + '%s'
    elif dbms == 'sqlite':
        return query_play_count_by_month + '?'


def build_query_play_count_for_duration(duration):
    condition = build_duration_condition(duration)
    return query_play_count.format(condition=condition)


def build_query_top_artists_for_duration_with_remaining(duration):
    query_top = build_query_top_artists_for_duration(duration)
    query_count = build_query_play_count_for_duration(duration)
    return query_top_artists_with_remaining.format(query_top=query_top,
                                                   query_play_count=query_count)


def build_query_top_artists_for_duration(duration):
    condition = build_duration_condition(duration)
    return query_top_artists.format(condition=condition) + add_limit()


def add_limit():
    clause = 'limit '
    if dbms == 'mysql':
        clause += '%s'
    elif dbms == 'sqlite':
        clause += '?'
    return clause


def build_query_top_albums_for_duration_with_remaining(duration):
    query_top = build_query_top_albums_for_duration(duration)
    query_count = build_query_play_count_for_duration(duration)
    return query_top_albums_with_remaining.format(query_top=query_top,
                                                  query_play_count=query_count)


def build_query_top_albums_for_duration(duration):
    condition = build_duration_condition(duration)
    return query_top_albums.format(condition=condition) + add_limit()


def build_query_top_tracks_for_duration_with_remaining(duration):
    query_top = build_query_top_tracks_for_duration(duration)
    query_count = build_query_play_count_for_duration(duration)
    return query_top_tracks_with_remaining.format(query_top=query_top,
                                                  query_play_count=query_count)


def build_query_top_tracks_for_duration(duration):
    condition = build_duration_condition(duration)
    return query_top_tracks.format(condition=condition) + add_limit()


def build_query_play_count_for_year():
    condition = build_year_condition()
    return query_play_count.format(condition=condition)


def build_query_top_artists_for_year_with_remaining():
    query_top = build_query_top_artists_for_year()
    query_count = build_query_play_count_for_year()
    return query_top_artists_with_remaining.format(query_top=query_top,
                                                   query_play_count=query_count)


def build_query_top_artists_for_year():
    condition = build_year_condition()
    return query_top_artists.format(condition=condition) + add_limit()


def build_query_top_albums_for_year_with_remaining():
    query_top = build_query_top_albums_for_year()
    query_count = build_query_play_count_for_year()
    return query_top_albums_with_remaining.format(query_top=query_top,
                                                  query_play_count=query_count)


def build_query_top_albums_for_year():
    condition = build_year_condition()
    return query_top_albums.format(condition=condition) + add_limit()


def build_query_top_tracks_for_year_with_remaining():
    query_top = build_query_top_tracks_for_year()
    query_count = build_query_play_count_for_year()
    return query_top_tracks_with_remaining.format(query_top=query_top,
                                                  query_play_count=query_count)


def build_query_top_tracks_for_year():
    condition = build_year_condition()
    return query_top_tracks.format(condition=condition) + add_limit()


def build_duration_condition(duration):
    condition = ''
    if duration.isdigit():
        if dbms == 'mysql':
            condition = 'and p.play_date > now() + interval - %s day'
        elif dbms == 'sqlite':
            condition =\
                'and date(p.play_date) > date(\'now\', \'-\' || ? || \' day\')'
    return condition


def build_year_condition():
    condition = ''
    if dbms == 'mysql':
        condition = 'and year(p.play_date) = %s'
    elif dbms == 'sqlite':
        condition = 'and strftime(\'%Y\', p.play_date) = ?'
    return condition
