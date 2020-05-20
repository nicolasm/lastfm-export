#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from enum import Enum

import pandas

from lfmdb.lfmdb import select
from queries.tops import build_query_top_artists_for_duration, \
    build_query_top_artists_for_year, build_query_top_albums_for_duration, \
    build_query_top_albums_for_year, build_query_top_tracks_for_duration, \
    build_query_top_tracks_for_year, build_query_play_count_for_duration, \
    build_query_play_count_for_year, build_query_play_count_by_month


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
    DurationArtist = (Top.Artist,
                      OverType.Duration,
                      'retrieve_top_artists_for_duration_as_dataframe')
    DurationAlbum = (Top.Album,
                     OverType.Duration,
                     'retrieve_top_albums_for_duration_as_dataframe')
    DurationTrack = (Top.Track,
                     OverType.Duration,
                     'retrieve_top_tracks_for_duration_as_dataframe')
    YearArtist = (Top.Artist,
                  OverType.Year,
                  'retrieve_top_artists_for_year_as_dataframe')
    YearAlbum = (Top.Album,
                 OverType.Year,
                 'retrieve_top_albums_for_year_as_dataframe')
    YearTrack = (Top.Track,
                 OverType.Year,
                 'retrieve_top_tracks_for_year_as_dataframe')

    def __init__(self, top, over_type, method):
        self.top = top
        self.over_type = over_type
        self.method = method

    def retrieve(self, agg_value, limit, remove_remaining=True):
        df = eval(self.method)(agg_value, limit)
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


def retrieve_play_count_by_month_as_dataframe(year):
    query = build_query_play_count_by_month()
    rows = select(query, (year,))
    df = pandas.DataFrame(rows, columns=['YearMonth', 'Month', 'PlayCount'], dtype='int64')
    df['YearMonth'] = pandas.to_datetime(df['YearMonth'], format='%Y-%m')
    df = df.sort_values(by='YearMonth')
    return df


def retrieve_total_play_count(nb_days):
    query = build_query_play_count_for_duration(nb_days)
    rows = select(query, (nb_days,))
    return rows[0]


def retrieve_total_play_count_for_year(for_year):
    query = build_query_play_count_for_year()
    rows = select(query, (for_year,))
    return rows[0]


def retrieve_top_artists_for_duration_as_dataframe(nb_days, limit):
    params = build_duration_params(nb_days, limit)
    query = build_query_top_artists_for_duration(nb_days)
    rows = select(query, params)
    return create_artists_dataframe(rows)


def retrieve_top_artists_for_year_as_dataframe(for_year, limit):
    query = build_query_top_artists_for_year()
    rows = select(query, (for_year, limit))
    return create_artists_dataframe(rows)


def create_artists_dataframe(rows):
    df = pandas.DataFrame(rows, columns=['Artist', 'PlayCount'], dtype='int64')
    df = df.sort_values(by='PlayCount', ascending=False)
    return df


def retrieve_top_albums_for_duration_as_dataframe(nb_days, limit):
    params = build_duration_params(nb_days, limit)
    query = build_query_top_albums_for_duration(nb_days)
    rows = select(query, params)
    return create_albums_dataframe(rows)


def retrieve_top_albums_for_year_as_dataframe(for_year, limit):
    query = build_query_top_albums_for_year()
    rows = select(query, (for_year, limit))
    return create_albums_dataframe(rows)


def create_albums_dataframe(rows):
    df = pandas.DataFrame(rows, columns=['Album', 'Artist', 'PlayCount'],
                          dtype='int64')
    df["ArtistAlbum"] = df["Artist"] + " - " + df["Album"]
    df = df.sort_values(by='PlayCount', ascending=False)
    return df


def retrieve_top_tracks_for_duration_as_dataframe(nb_days, limit):
    params = build_duration_params(nb_days, limit)
    query = build_query_top_tracks_for_duration(nb_days)
    rows = select(query, params)
    return create_tracks_dataframe(rows)


def build_duration_params(nb_days, limit):
    params = (limit,)
    if nb_days.isdigit():
        params = (nb_days,) + params
    return params


def retrieve_top_tracks_for_year_as_dataframe(for_year, limit):
    query = build_query_top_tracks_for_year()
    rows = select(query, (for_year, limit))
    return create_tracks_dataframe(rows)


def create_tracks_dataframe(rows):
    df = pandas.DataFrame(rows,
                          columns=['Track', 'Artist', 'Album', 'PlayCount'],
                          dtype='int64')
    df["ArtistAlbumTrack"] = df["Artist"] + " - " + df["Album"] + " - " + df[
        "Track"]
    df = df.sort_values(by='PlayCount', ascending=False);
    return df
