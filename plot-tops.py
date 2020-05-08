#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
from pathlib import Path

import MySQLdb
import matplotlib.pyplot as plt
import telegram
from PIL import Image

from lastfmConf.lastfmConf import get_lastfm_conf
from lastfmPandas.lastfmPandas import DataFrameColumn, \
    AggregationType, OverType
from lastfmPlot.lastfmPlot import PlotType, Duration, Year

conf = get_lastfm_conf()

mysql = MySQLdb.connect(
    user=conf['lastfm']['db']['user'], passwd=conf['lastfm']['db']['password'],
    db=conf['lastfm']['db']['db_name'], charset='utf8')
mysql_cursor = mysql.cursor()


def parse_args():
    parser = argparse.ArgumentParser()
    now = datetime.now()
    years = range(2006, now.year + 1)

    time_periods = [e.name for e in Duration]
    time_periods.extend(str(y) for y in years)

    parser.add_argument('-t', '--timePeriod', nargs='?', choices=time_periods,
                        default=str(now.year))
    parser.add_argument('-a', '--aggregationType', nargs='?',
                        choices=[a.name for a in AggregationType],
                        default=AggregationType.YEAR_ALBUM.name)
    parser.add_argument('-p', '--plotType', nargs='?',
                        choices=[p.name for p in PlotType],
                        default=PlotType.PIE.name)
    parser.add_argument('-c', '--dataFrameColumn', nargs='?',
                        choices=[c.name for c in DataFrameColumn],
                        default=DataFrameColumn.ArtistAlbum.name)

    return parser.parse_args()


def send_photo(bio, caption):
    bio.seek(0)
    bot = telegram.Bot(token=conf['telegram']['token'])
    bot.send_photo(conf['telegram']['chatId'], photo=bio, caption=caption)


def plot(time_period, agg_type, plot_type, data_frame_column):
    label = time_period.get_label()
    Path('./tops/%ss/%s' % (agg_type.get_over_type(), label)).mkdir(
        parents=True, exist_ok=True)
    df = agg_type.retrieve(mysql_cursor,
                           time_period.get_value(), 20)
    bio = plot_type.plot(df, data_frame_column)
    plt.close()
    bio.seek(0)
    image = Image.open(bio)

    save_plot(agg_type, image, label, plot_type)
    send_via_telegram(agg_type, bio, label, plot_type)

    bio.close()


def save_plot(agg_type, image, label, plot_type):
    if conf['plot']['saveEnabled']:
        image.save(
            'tops/{over_type}s/{label}/top-{agg_type}s-{label}-{plot_type}.png'.format(
                over_type=agg_type.get_over_type(), agg_type=agg_type.get_top(),
                label=label, plot_type=plot_type.get_name()))


def send_via_telegram(agg_type, bio, label, plot_type):
    if conf['plot']["sendViaTelegram"]:
        send_photo(bio, 'Top {agg_type}s {label} as {plot_type}'.format(
            agg_type=agg_type.get_top(),
            label=label, plot_type=plot_type.get_name()))


def get_time_period(args):
    time_period = None
    if agg_type.over_type == OverType.DURATION:
        time_period = Duration.from_value(args.timePeriod)
    elif agg_type.over_type == OverType.YEAR:
        time_period = Year(args.timePeriod)
    return time_period


args = parse_args()

agg_type = AggregationType.from_value(args.aggregationType)
plot_type = PlotType.from_value(args.plotType)
data_frame_column = DataFrameColumn.from_value(args.dataFrameColumn)

plot(get_time_period(args), agg_type, plot_type, data_frame_column)
