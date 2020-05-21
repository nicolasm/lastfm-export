from datetime import datetime

import pandas

from queries.artist_counts import get_artist_counts_query_overall, \
    get_artist_counts_query_year
from lfmdb.lfmdb import select
from lfmconf.lfmconf import get_lastfm_conf

conf = get_lastfm_conf()
start_year = conf['lastfm']['service']['startYear']
now = datetime.now()
years = range(start_year, now.year + 1)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
          'Nov', 'Dec']


def retrieve_artist_counts(artist_name):
    queries = get_artist_counts_query_overall()

    rows = select(queries[0], (artist_name,))
    df_albums = pandas.DataFrame(rows,
                                 columns=['AlbumName', 'PlayCount'],
                                 dtype='int64')
    df_albums = df_albums.sort_values(by='PlayCount')

    rows = select(queries[1], (artist_name,))
    df_artist = pandas.DataFrame(rows,
                                 columns=['Year', 'PlayCount'],
                                 dtype='int64')
    df_artist['Year'] = df_artist['Year'].astype('int')
    df_artist = df_artist.set_index('Year')

    df_artist = df_artist.reindex(years, fill_value=0)\
                         .rename_axis('Year')\
                         .reset_index()

    df_artist = df_artist.sort_values(by='Year', ascending=False)

    return df_albums, df_artist


def retrieve_artist_counts_for_year(artist_name, year):
    queries = get_artist_counts_query_year()

    rows = select(queries[0], (artist_name, year))
    df_albums = pandas.DataFrame(rows,
                                 columns=['AlbumName', 'PlayCount'],
                                 dtype='int64')
    df_albums = df_albums.sort_values(by='PlayCount')

    rows = select(queries[1], (artist_name, year))
    df_artist = pandas.DataFrame(rows,
                                 columns=['YearMonth', 'PlayCount'],
                                 dtype='int64')
    df_artist = df_artist.set_index('YearMonth')

    year_months = ['%s-%02d' % (year, m) for m in range(1, 13)]

    df_artist = df_artist.reindex(year_months, fill_value=0) \
        .rename_axis('YearMonth') \
        .reset_index()

    df_artist = df_artist.sort_values(by='YearMonth')

    return df_albums, df_artist


def month_name(month):
    return months[month - 1]
