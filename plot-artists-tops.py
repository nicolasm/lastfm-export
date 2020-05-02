#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

import MySQLdb
import colorlover as cl
import matplotlib.pyplot as plt

from pathlib import Path

import netrcfile
from lastfmPandas.lastfmPandas import retrieve_top_artists_as_dataframe, \
    retrieve_top_albums_as_dataframe, \
    retrieve_top_artists_for_year_as_dataframe, \
    retrieve_top_albums_for_year_as_dataframe

login = netrcfile.retrieve_from_netrc('lastfm.mysql')

mysql = MySQLdb.connect(
    user=login[0], passwd=login[2], db=login[1], charset='utf8')
mysql_cursor = mysql.cursor()

colors = cl.to_numeric(cl.scales['10']['qual']['Set3'])

# df = retrieve_play_count_by_month_as_dataframe(mysql_cursor)
# df.head()

int_colors = []
for color in colors:
    int_colors.append((int(color[0]), int(color[1]), int(color[2])))

selected_colors = []
for color in int_colors:
    selected_colors.append('#%02x%02x%02x' % color)


def plot_pie(df, legend_column):
    df.plot.pie(y='PlayCount', labels=df['PlayCount'], figsize=(12, 5),
                legend=True, colors=selected_colors)
    plt.legend(df[legend_column], loc="center left",
               bbox_to_anchor=(1, 0, 0.5, 1))


def plot_barh(df, xcolumn):
    ax = df.plot.barh(x=xcolumn, y='PlayCount', figsize=(20, 5), rot=0,
                      color=selected_colors)
    # ax.legend()

    # create a list to collect the plt.patches data
    totals = []

    # find the values and append to list
    for i in ax.patches:
        totals.append(i.get_width())

    for i in ax.patches:
        # get_width pulls left or right; get_y pushes up or down
        ax.text(i.get_width() + .3, i.get_y(), i.get_width(), fontsize=15,
                color='dimgrey')


def plot_tops_durations():
    nbDays = ['7', '30', '90', '120', '180', '365', 'null']

    for duration in nbDays:
        suffix = 'overall'
        folder = suffix
        if duration != 'null':
            folder = duration
            suffix = 'for-the-last-%s-days' % duration

        Path('./tops/durations/%s' % folder).mkdir(parents=True, exist_ok=True)

        df = retrieve_top_artists_as_dataframe(mysql_cursor, duration, 10)
        df = df[df.Artist != 'Remaining artists']
        plot_pie(df, 'Artist')
        plt.savefig('tops/durations/%s/top-artists-%s-pie.png' % (folder, suffix),
                    format='png', dpi=150)
        plt.close()

        df = retrieve_top_artists_as_dataframe(mysql_cursor, duration, 20)
        df = df[df.Artist != 'Remaining artists']
        plot_barh(df, 'Artist')
        plt.savefig('tops/durations/%s/top-artists-%s-barh.png' % (folder, suffix),
                    format='png', dpi=150)
        plt.close()

        df = retrieve_top_albums_as_dataframe(mysql_cursor, duration, 10)
        df = df[df.Album != 'Remaining albums']
        plot_pie(df, 'ArtistAlbum')
        plt.savefig('tops/durations/%s/top-albums-%s-pie.png' % (folder, suffix),
                    format='png', dpi=150)
        plt.close()

        df = retrieve_top_albums_as_dataframe(mysql_cursor, duration, 20)
        df = df[df.Album != 'Remaining albums']
        plot_barh(df, 'Album')
        plt.savefig('tops/durations/%s/top-albums-%s-barh.png' % (folder, suffix),
                    format='png', dpi=150)
        plt.close()


def plot_tops_years():
    now = datetime.now()
    for x in range(2008, now.year + 1):
        year = str(x)

        Path('./tops/years/%s' % year).mkdir(parents=True, exist_ok=True)

        df = retrieve_top_artists_for_year_as_dataframe(mysql_cursor, year, 10)
        df = df[df.Artist != 'Remaining artists']
        plot_pie(df, 'Artist')
        plt.savefig('tops/years/{year}/top-artists-{year}-pie.png'.format(year=year),
                    format='png', dpi=150)
        plt.close()

        df = retrieve_top_artists_for_year_as_dataframe(mysql_cursor, year, 20)
        df = df[df.Artist != 'Remaining artists']
        plot_barh(df, 'Artist')
        plt.savefig('tops/years/{year}/top-artists-{year}-barh.png'.format(year=year),
                    format='png', dpi=150)
        plt.close()

        df = retrieve_top_albums_for_year_as_dataframe(mysql_cursor, year, 10)
        df = df[df.Album != 'Remaining albums']
        plot_pie(df, 'Album')
        plt.savefig('tops/years/{year}/top-albums-{year}-pie.png'.format(year=year),
                    format='png', dpi=150)
        plt.close()

        df = retrieve_top_albums_for_year_as_dataframe(mysql_cursor, year, 20)
        df = df[df.Album != 'Remaining albums']
        plot_barh(df, 'Album')
        plt.savefig('tops/years/{year}/top-albums-{year}-barh.png'.format(year=year),
                    format='png', dpi=150)
        plt.close()


plot_tops_durations()
# plot_tops_years()
