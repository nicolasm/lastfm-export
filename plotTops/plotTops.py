#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

import MySQLdb
import matplotlib.pyplot as plt
import telegram

from lastfmConf.lastfmConf import get_lastfm_conf

conf = get_lastfm_conf()

mysql = MySQLdb.connect(
    user=conf['lastfm']['db']['user'], passwd=conf['lastfm']['db']['password'],
    db=conf['lastfm']['db']['dbName'], charset='utf8')
mysql_cursor = mysql.cursor()


def send_photo(bio, caption):
    bio.seek(0)
    bot = telegram.Bot(token=conf['telegram']['token'])
    bot.send_photo(conf['telegram']['chatId'], photo=bio, caption=caption)


def plot(time_period, agg_type, plot_type, data_frame_column):
    label = time_period.get_label()
    Path('./tops/%ss/%s' % (agg_type.get_over_type(), label.lower())).mkdir(
        parents=True, exist_ok=True)
    df = agg_type.retrieve(mysql_cursor,
                           time_period.get_value(), 20)
    bio = plot_type.plot(df, data_frame_column)
    plt.close()
    return bio


def save_plot(agg_type, image, label, plot_type):
    if conf['plot']['saveEnabled']:
        image.save(
            'tops/{over_type}s/{label}/top-{agg_type}s-{label}-{plot_type}.png'.format(
                over_type=agg_type.get_over_type(), agg_type=agg_type.get_top(),
                label=label.lower(), plot_type=plot_type.get_name()))


def send_via_telegram(agg_type, bio, label, plot_type):
    if conf['plot']["sendViaTelegram"]:
        send_photo(bio, 'Top {agg_type}s {label} as {plot_type}'.format(
            agg_type=agg_type.get_top(),
            label=label, plot_type=plot_type.get_name()))
