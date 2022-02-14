#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
from datetime import datetime
from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from lfmconf.lfmconf import get_lastfm_conf
from lfmpandas.artist_counts import retrieve_artist_counts, \
    retrieve_artist_counts_for_year
from lfmpandas.lfmpandas import retrieve_play_count_by_month_as_dataframe

conf = get_lastfm_conf()


def plot_top(time_period, agg_type, plot_type, data_frame_column,
             with_remaining):
    label = time_period.get_label()
    Path('./tops/%ss/%s' % (agg_type.get_over_type(), label.lower())).mkdir(
        parents=True, exist_ok=True)
    df = agg_type.retrieve(time_period.get_value(), 20, with_remaining)
    bio = plot_type.plot(df, data_frame_column)
    plt.close()
    return bio


def plot_play_counts_last_n_years(last_n_years):
    now = datetime.now()
    years = range(conf['lastfm']['service']['startYear'], now.year + 1)
    df_years = pd.DataFrame()
    for year in years[-last_n_years:]:
        df = retrieve_play_count_by_month_as_dataframe(str(year))
        if df_years.get('Month') is None:
            df_years["Month"] = df.Month
        df_years[str(year)] = df.PlayCount

    df_years.plot(x='Month', kind='bar', width=0.7)
    plt.legend(loc="upper right")

    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=150, bbox_inches='tight')
    plt.close()

    return bio


def plot_play_counts_by_month():
    now = datetime.now()
    years = range(conf['lastfm']['service']['startYear'], now.year + 1)

    nb_cols = 4
    nb_rows = ceil(len(years) / nb_cols)

    f, ax_array = plt.subplots(nb_rows, nb_cols, figsize=(20,20))

    year_index = 0
    for i in range(0, nb_rows):
        for j in range(0, nb_cols):
            if year_index < len(years):
                year = str(years[year_index])
                df = retrieve_play_count_by_month_as_dataframe(year)

                ax_array[i, j].plot(df.Month, df.PlayCount)
                ax_array[i, j].set_title(year)
                year_index = year_index + 1

    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=150, bbox_inches='tight')
    plt.close()

    return bio


def plot_artist_counts(artist_name):
    dfs = retrieve_artist_counts(artist_name)

    f, ax_array = plt.subplots(2, 1, figsize=(10,10))

    ax_array[0].barh(dfs[0].AlbumName, dfs[0].PlayCount, color='pink')
    ax_array[1].barh(dfs[1].Year, dfs[1].PlayCount, color='pink')
    ax_array[1].set_yticks(dfs[1].Year)

    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=150, bbox_inches='tight')
    plt.close()

    return bio


def plot_artist_counts_for_year(artist_name, year):
    dfs = retrieve_artist_counts_for_year(artist_name, str(year))

    f, ax_array = plt.subplots(2, 1, figsize=(10,10))

    ax_array[0].barh(dfs[0].AlbumName, dfs[0].PlayCount, color='pink')
    ax_array[1].barh(dfs[1].YearMonth, dfs[1].PlayCount, color='pink')
    ax_array[1].set_yticks(dfs[1].YearMonth)

    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=150, bbox_inches='tight')
    plt.close()

    return bio
