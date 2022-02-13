#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
from datetime import datetime

from PIL import Image

from lfmconf.lfmconf import get_lastfm_conf
from lfmpandas.lfmpandas import DataFrameColumn, \
    AggregationType, OverType
from plot.plot import plot_top
from plottop.plotop import PlotType, Duration, Year

logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s %(levelname)s %(message)s'
)

conf = get_lastfm_conf()


def parse_args():
    parser = argparse.ArgumentParser()
    now = datetime.now()
    years = range(conf['lastfm']['service']['startYear'], now.year + 1)

    time_periods = [e.get_value() for e in Duration]
    time_periods.extend(str(y) for y in years)

    parser.add_argument('-t', '--timePeriod', nargs='?', type=str,
                        choices=time_periods,
                        default=str(now.year))
    parser.add_argument('-a', '--aggregationType', nargs='?',
                        choices=[a.name for a in AggregationType],
                        default=AggregationType.YearAlbum.name)
    parser.add_argument('-p', '--plotType', nargs='?',
                        choices=[p.name for p in PlotType],
                        default=PlotType.Pie.name)
    parser.add_argument('-c', '--dataFrameColumn', nargs='?',
                        choices=[c.name for c in DataFrameColumn],
                        default=DataFrameColumn.ArtistAlbum.name)
    parser.add_argument('-r', '--withRemaining',
                        dest='withRemaining',
                        action='store_true')
    parser.add_argument('-w', '--withoutRemaining',
                        dest='withRemaining',
                        action='store_false')
    parser.set_defaults(with_remaining=False)

    return parser.parse_args()


def save_plot(agg_type, image, label, plot_type):
    image.save(
        'tops/{over_type}s/{label}/top-{agg_type}s-{label}-{plot_type}.png'
            .format(over_type=agg_type.get_over_type(),
                    agg_type=agg_type.get_top(),
                    label=label.lower(),
                    plot_type=plot_type.get_name()))


def get_time_period(agg_type, value):
    time_period = None
    if agg_type.over_type == OverType.Duration:
        time_period = Duration.from_value(value)
    elif agg_type.over_type == OverType.Year:
        time_period = Year(value)
    return time_period


args = parse_args()
agg_type = AggregationType.from_value(args.aggregationType)
plot_type = PlotType.from_value(args.plotType)
data_frame_column = DataFrameColumn.from_value(args.dataFrameColumn)
with_remaining = args.withRemaining

time_period = get_time_period(agg_type, args.timePeriod)
bio = plot_top(time_period,
               agg_type,
               plot_type,
               data_frame_column,
               with_remaining)

bio.seek(0)
image = Image.open(bio)
save_plot(agg_type, image, time_period.get_label(), plot_type)

bio.close()
