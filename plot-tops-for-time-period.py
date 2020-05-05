#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path

import MySQLdb
import matplotlib.pyplot as plt
from PIL import Image

import netrcfile
from lastfmPandas.lastfmPandas import DataFrameColumn, \
    AggregationType, OverType
from lastfmPlot.lastfmPlot import PlotType, Duration, Year

import argparse

login = netrcfile.retrieve_from_netrc('lastfm.mysql')

mysql = MySQLdb.connect(
    user=login[0], passwd=login[2], db=login[1], charset='utf8')
mysql_cursor = mysql.cursor()


def parse_args():
    parser = argparse.ArgumentParser()
    now = datetime.now()
    years = range(2006, now.year + 1)

    time_periods = [e.name for e in Duration]
    time_periods.extend(str(y) for y in years)

    parser.add_argument('timePeriod', choices=time_periods)
    parser.add_argument('aggregationType', choices=[a.name for a in AggregationType])
    parser.add_argument('plotType', choices=[p.name for p in PlotType])
    parser.add_argument('dataFrameColumn', choices=[c.name for c in DataFrameColumn])

    return parser.parse_args()


def plot(time_period, agg_type, plot_type, data_frame_column):
    label = time_period.get_label()
    Path('./tops/%ss/%s' % (agg_type.get_over_type(), label)).mkdir(
        parents=True, exist_ok=True)
    df = agg_type.retrieve(mysql_cursor,
                           time_period.get_value(), 20)
    buffer = plot_type.plot(df, data_frame_column)
    plt.close()
    buffer.seek(0)
    image = Image.open(buffer)
    image.save(
        'tops/{over_type}s/{label}/top-{agg_type}s-{label}-{plot_type}.png'.format(
            over_type=agg_type.get_over_type(), agg_type=agg_type.get_top(),
            label=label, plot_type=plot_type.get_name()))
    buffer.close()


args = parse_args()

agg_type = AggregationType.from_value(args.aggregationType)
plot_type = PlotType.from_value(args.plotType)
data_frame_column = DataFrameColumn.from_value(args.dataFrameColumn)


def get_time_period(args):
    time_period = None
    if agg_type.over_type == OverType.DURATION:
        time_period = Duration.from_value(args.timePeriod)
    elif agg_type.over_type == OverType.YEAR:
        time_period = Year(args.timePeriod)
    return time_period


plot(get_time_period(args), agg_type, plot_type, data_frame_column)
