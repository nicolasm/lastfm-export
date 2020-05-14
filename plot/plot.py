#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
from datetime import datetime
from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt

from lfmconf.lfmconf import get_lastfm_conf
from lfmpandas.lfmpandas import retrieve_play_count_by_month_as_dataframe

conf = get_lastfm_conf()


def plot_top(time_period, agg_type, plot_type, data_frame_column):
    label = time_period.get_label()
    Path('./tops/%ss/%s' % (agg_type.get_over_type(), label.lower())).mkdir(
        parents=True, exist_ok=True)
    df = agg_type.retrieve(time_period.get_value(), 20)
    bio = plot_type.plot(df, data_frame_column)
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
    plt.savefig(bio, format='png', dpi=150)
    plt.close()

    return bio
