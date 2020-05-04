#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pandas

query_top = """
with top as (
    select v.*
    from (select @{function_name} := {function_value} p) parm, view_top_{entity}s_{function_name} v
    limit {limit}
),
total_count as (
    select v.play_count
    from view_play_count v
)

select t.*
from top t
"""

queries_top_for_function = {}
queries_top_for_function['Artist'] = query_top + \
                                     """
                                     union all
                                     select 'Remaining {entity}s' as {entity}_name,
                                     ((select tc.play_count from total_count tc)
                                     -
                                     (select sum(play_count) from top)) as play_count

                                     """

queries_top_for_function['Album'] = query_top + \
                                    """
                                    union all
                                    select 'Remaining {entity}s' as {entity}_name,
                                    '...' as album_name,
                                    ((select tc.play_count from total_count tc)
                                    -
                                    (select sum(play_count) from top)) as play_count

                                    """

queries_top_for_function['Track'] = query_top + \
                                    """
                                    union all
                                    select 'Remaining {entity}s' as {entity}_name,
                                    '...' as artist_name,
                                    '...' as album_name,
                                    ((select tc.play_count from total_count tc)
                                    -
                                    (select sum(play_count) from top)) as play_count

                                    """

query_total_count = 'select v.* from (select @nb_days:=%s p) parm, view_play_count v'
query_total_count_for_year = 'select v.* from (select @for_year:=%s p) parm, view_play_count_for_year v'


def retrieve_play_count_by_month_as_dataframe(cursor, year):
    cursor.execute('select * from view_play_count_by_month v where substr(v.month, 1, 4) = %s' % year)
    rows = cursor.fetchall()
    df = pandas.DataFrame([[ij for ij in i] for i in rows])
    df.rename(columns={0: 'Month', 1: 'PlayCount'}, inplace=True)
    df['Month'] = pandas.to_datetime(df['Month'], format='%Y-%m')
    df = df.sort_values(by='Month')
    return df


def retrieve_play_count_by_day_as_dataframe(cursor):
    select = 'select date_format(p.play_date, \'%y-%m-%d\') as day, count(p.id) as count from play p'
    where = 'where p.play_date > date_add(CURRENT_TIMESTAMP, interval -30 day)'
    group_and_order = 'group by day order by day desc'
    cursor.execute('%s %s %s' % (select, where, group_and_order))
    rows = cursor.fetchall()

    df = pandas.DataFrame([[ij for ij in i] for i in rows])
    df.rename(columns={0: 'Day', 1: 'PlayCount'}, inplace=True)
    df['Day'] = pandas.to_datetime(df['Day'], format='%y-%m-%d')
    return df.head(30)


def retrieve_recent_plays_as_dataframe(cursor):
    cursor.execute('select * from view_plays')
    rows = cursor.fetchall()

    df = pandas.DataFrame([[ij for ij in i] for i in rows])
    df = df.drop(4, 1)
    df.rename(
        columns={0: 'Track nb', 1: 'Track', 2: 'Artist', 3: 'Album', 5: 'Date'},
        inplace=True);
    return df.head(30)


def retrieve_total_play_count(cursor, nb_days):
    cursor.execute(query_total_count % nb_days)
    return cursor.fetchone()[0]


def retrieve_total_play_count_for_year(cursor, for_year):
    cursor.execute(query_total_count % for_year)
    return cursor.fetchone()[0]


def retrieve_top_artists_as_dataframe(cursor, nb_days, limit):
    cursor.execute(
        queries_top_for_function['Artist'].format(function_name='for_nb_days',
                                                  entity='artist',
                                                  function_value=nb_days,
                                                  limit=limit))
    return create_artists_dataframe(cursor)


def retrieve_top_artists_for_year_as_dataframe(cursor, for_year, limit):
    cursor.execute(
        queries_top_for_function['Artist'].format(function_name='for_year',
                                                  entity='artist',
                                                  function_value=for_year,
                                                  limit=limit))
    return create_artists_dataframe(cursor)


def create_artists_dataframe(cursor):
    rows = cursor.fetchall()
    df = pandas.DataFrame(rows, columns=['Artist', 'PlayCount'], dtype='int64')
    df = df.sort_values(by='PlayCount', ascending=False)
    return df


def retrieve_top_albums_as_dataframe(cursor, nb_days, limit):
    cursor.execute(
        queries_top_for_function['Album'].format(function_name='for_nb_days',
                                                 entity='album',
                                                 function_value=nb_days,
                                                 limit=limit))
    return create_albums_dataframe(cursor)


def retrieve_top_albums_for_year_as_dataframe(cursor, for_year, limit):
    cursor.execute(
        queries_top_for_function['Album'].format(function_name='for_year',
                                                 entity='album',
                                                 function_value=for_year,
                                                 limit=limit))
    return create_albums_dataframe(cursor)


def create_albums_dataframe(cursor):
    rows = cursor.fetchall()
    df = pandas.DataFrame(rows, columns=['Album', 'Artist', 'PlayCount'],
                          dtype='int64')
    df["ArtistAlbum"] = df["Artist"] + " - " + df["Album"]
    df = df.sort_values(by='PlayCount', ascending=False)
    return df


def retrieve_top_tracks_as_dataframe(cursor, nb_days, limit):
    cursor.execute(
        queries_top_for_function['Track'].format(function_name='for_nb_days',
                                                 entity='track',
                                                 function_value=nb_days,
                                                 limit=limit))
    return create_tracks_dataframe(cursor)


def retrieve_top_tracks_for_year_as_dataframe(cursor, for_year, limit):
    cursor.execute(
        queries_top_for_function['Track'].format(function_name='for_year',
                                                 entity='track',
                                                 function_value=for_year,
                                                 limit=limit))
    return create_tracks_dataframe(cursor)


def create_tracks_dataframe(cursor):
    rows = cursor.fetchall()
    df = pandas.DataFrame(rows,
                          columns=['Track', 'Artist', 'Album', 'PlayCount'],
                          dtype='int64')
    df["ArtistAlbumTrack"] = df["Artist"] + " - " + df["Album"] + " - " + df[
        "Track"]
    df = df.sort_values(by='PlayCount', ascending=False);
    return df
