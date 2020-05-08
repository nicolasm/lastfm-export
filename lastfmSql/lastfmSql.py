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
    limit {limit}
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
    limit {limit}
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
    limit {limit}
"""

query_play_count = """
    select count(p.id) as play_count
    from play p
    where 1 = 1
    {condition}
"""


def build_query_play_count_for_duration(duration):
    condition = build_duration_condition(duration)
    return query_play_count.format(condition=condition)


def build_query_top_artists_for_duration_with_remaining(duration, limit):
    query_top = build_query_top_artists_for_duration(duration, limit)
    query_count = build_query_play_count_for_duration(duration)
    return query_top_artists_with_remaining.format(query_top=query_top,
                                                   query_play_count=query_count)


def build_query_top_artists_for_duration(duration, limit):
    condition = build_duration_condition(duration)
    return query_top_artists.format(condition=condition, limit=limit)


def build_query_top_albums_for_duration_with_remaining(duration, limit):
    query_top = build_query_top_albums_for_duration(duration, limit)
    query_count = build_query_play_count_for_duration(duration)
    return query_top_albums_with_remaining.format(query_top=query_top,
                                                   query_play_count=query_count)


def build_query_top_albums_for_duration(duration, limit):
    condition = build_duration_condition(duration)
    return query_top_albums.format(condition=condition, limit=limit)


def build_query_top_tracks_for_duration_with_remaining(duration, limit):
    query_top = build_query_top_tracks_for_duration(duration, limit)
    query_count = build_query_play_count_for_duration(duration)
    return query_top_tracks_with_remaining.format(query_top=query_top,
                                                   query_play_count=query_count)


def build_query_top_tracks_for_duration(duration, limit):
    condition = build_duration_condition(duration)
    return query_top_tracks.format(condition=condition, limit=limit)


def build_query_play_count_for_year(year):
    condition = build_year_condition(year)
    return query_play_count.format(condition=condition)


def build_query_top_artists_for_year_with_remaining(year, limit):
    query_top = build_query_top_artists_for_year(year, limit)
    query_count = build_query_play_count_for_year(year)
    return query_top_artists_with_remaining.format(query_top=query_top,
                                                   query_play_count=query_count)


def build_query_top_artists_for_year(year, limit):
    condition = build_year_condition(year)
    return query_top_artists.format(condition=condition, limit=limit)


def build_query_top_albums_for_year_with_remaining(year, limit):
    query_top = build_query_top_albums_for_year(year, limit)
    query_count = build_query_play_count_for_year(year)
    return query_top_albums_with_remaining.format(query_top=query_top,
                                                   query_play_count=query_count)


def build_query_top_albums_for_year(year, limit):
    condition = build_year_condition(year)
    return query_top_albums.format(condition=condition, limit=limit)


def build_query_top_tracks_for_year_with_remaining(year, limit):
    query_top = build_query_top_tracks_for_year(year, limit)
    query_count = build_query_play_count_for_year(year)
    return query_top_tracks_with_remaining.format(query_top=query_top,
                                                  query_play_count=query_count)


def build_query_top_tracks_for_year(year, limit):
    condition = build_year_condition(year)
    return query_top_tracks.format(condition=condition, limit=limit)


def build_duration_condition(duration):
    condition = ''
    if duration:
        condition = 'and p.play_date > now() + interval - %s day' % duration
    return condition


def build_year_condition(year):
    condition = ''
    if year:
        condition = 'and year(p.play_date) = %s' % year
    return condition
