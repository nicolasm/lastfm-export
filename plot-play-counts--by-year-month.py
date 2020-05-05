#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from math import ceil
from pathlib import Path

import MySQLdb
import matplotlib.pyplot as plt

import netrcfile
from lastfmPandas.lastfmPandas import retrieve_play_count_by_month_as_dataframe

login = netrcfile.retrieve_from_netrc('lastfm.mysql')

mysql = MySQLdb.connect(
    user=login[0], passwd=login[2], db=login[1], charset='utf8')
mysql_cursor = mysql.cursor()


def plot_play_counts_by_month():
    now = datetime.now()
    years = range(2006, now.year + 1)

    nb_cols = 4
    nb_rows = ceil(len(years) / nb_cols)

    f, ax_array = plt.subplots(nb_rows, nb_cols, figsize=(20,20))

    year_index = 0
    for i in range(0, nb_rows):
        for j in range(0, nb_cols):
            if year_index < len(years):
                year = str(years[year_index])
                df = retrieve_play_count_by_month_as_dataframe(mysql_cursor, year)

                ax_array[i, j].plot(df.Month, df.PlayCount)
                ax_array[i, j].set_title(year)
                year_index = year_index + 1

    Path('./tops').mkdir(parents=True, exist_ok=True)
    plt.savefig('tops/play-count-by-month.png', format='png', dpi=150)
    plt.close()


plot_play_counts_by_month()
