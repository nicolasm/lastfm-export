#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from enum import Enum

import pandas

from lastfmSql.lastfmSql import build_query_top_artists_for_duration, \
    build_query_top_artists_for_year, build_query_top_albums_for_duration, \
    build_query_top_albums_for_year, build_query_top_tracks_for_duration, \
    build_query_top_tracks_for_year, build_query_play_count_for_duration, \
    build_query_play_count_for_year


class DataFrameColumn(Enum):
    Artist = 1
    Album = 2
    ArtistAlbum = 3
    Track = 4
    ArtistAlbumTrack = 5

    @staticmethod
    def from_value(str_value):
        for e in DataFrameColumn:
            if e.name == str_value:
                return e


class Top(Enum):
    Artist = [DataFrameColumn.Artist]
    Album = [DataFrameColumn.Album, DataFrameColumn.ArtistAlbum]
    Track = [DataFrameColumn.Track, DataFrameColumn.ArtistAlbumTrack]

    def __init__(self, columns):
        self.columns = columns

    @staticmethod
    def from_value(str_value):
        for e in Top:
            if e.name == str_value:
                return e


class OverType(Enum):
    Duration = 1
    Year = 2


class AggregationType(Enum):
    DurationArtist = (Top.Artist, OverType.Duration, 'retrieve_top_artists_as_dataframe')
    DurationAlbum = (Top.Album, OverType.Duration, 'retrieve_top_albums_as_dataframe')
    DurationTrack = (Top.Track, OverType.Duration, 'retrieve_top_tracks_as_dataframe')
    YearArtist = (Top.Artist, OverType.Year, 'retrieve_top_artists_for_year_as_dataframe')
    YearAlbum = (Top.Album, OverType.Year, 'retrieve_top_albums_for_year_as_dataframe')
    YearTrack = (Top.Track, OverType.Year, 'retrieve_top_tracks_for_year_as_dataframe')

    def __init__(self, top, over_type, method):
        self.top = top
        self.over_type = over_type
        self.method = method

    def retrieve(self, cursor, agg_value, limit, remove_remaining=True):
        df = eval(self.method)(cursor, agg_value, limit)
        if remove_remaining:
            df = df[df[self.top.name.title()] != 'Remaining %ss' % self.get_top()]
        return df

    def get_top(self):
        return self.top.name.lower()

    def get_over_type(self):
        return self.over_type.name.lower()

    @staticmethod
    def from_value(str):
        for e in AggregationType:
            if e.name == str:
                return e


def retrieve_play_count_by_month_as_dataframe(cursor, year):
    cursor.execute('select * from view_play_count_by_month v where substr(v.yr_month, 1, 4) = %s' % year)
    rows = cursor.fetchall()
    df = pandas.DataFrame(rows, columns=['YearMonth', 'Month', 'PlayCount'], dtype='int64')
    df['YearMonth'] = pandas.to_datetime(df['YearMonth'], format='%Y-%m')
    df = df.sort_values(by='YearMonth')
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
    cursor.execute(build_query_play_count_for_duration(nb_days))
    return cursor.fetchone()[0]


def retrieve_total_play_count_for_year(cursor, for_year):
    cursor.execute(build_query_play_count_for_year(for_year))
    return cursor.fetchone()[0]


def retrieve_top_artists_as_dataframe(cursor, nb_days, limit):
    cursor.execute(build_query_top_artists_for_duration(nb_days, limit))
    return create_artists_dataframe(cursor)


def retrieve_top_artists_for_year_as_dataframe(cursor, for_year, limit):
    cursor.execute(build_query_top_artists_for_year(for_year, limit))
    return create_artists_dataframe(cursor)


def create_artists_dataframe(cursor):
    rows = cursor.fetchall()
    df = pandas.DataFrame(rows, columns=['Artist', 'PlayCount'], dtype='int64')
    df = df.sort_values(by='PlayCount', ascending=False)
    return df


def retrieve_top_albums_as_dataframe(cursor, nb_days, limit):
    cursor.execute(build_query_top_albums_for_duration(nb_days, limit))
    return create_albums_dataframe(cursor)


def retrieve_top_albums_for_year_as_dataframe(cursor, for_year, limit):
    cursor.execute(build_query_top_albums_for_year(for_year, limit))
    return create_albums_dataframe(cursor)


def create_albums_dataframe(cursor):
    rows = cursor.fetchall()
    df = pandas.DataFrame(rows, columns=['Album', 'Artist', 'PlayCount'],
                          dtype='int64')
    df["ArtistAlbum"] = df["Artist"] + " - " + df["Album"]
    df = df.sort_values(by='PlayCount', ascending=False)
    return df


def retrieve_top_tracks_as_dataframe(cursor, nb_days, limit):
    cursor.execute(build_query_top_tracks_for_duration(nb_days, limit))
    return create_tracks_dataframe(cursor)


def retrieve_top_tracks_for_year_as_dataframe(cursor, for_year, limit):
    cursor.execute(build_query_top_tracks_for_year(for_year, limit))
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
