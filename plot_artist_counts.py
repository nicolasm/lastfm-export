#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
from pathlib import Path

from PIL import Image
from slugify import slugify

from plot.plot import plot_artist_counts, plot_artist_counts_for_year

Path('./tops').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s %(levelname)s %(message)s'
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--artist', nargs=1, type=str)
    return parser.parse_args()


args = parse_args()
artist = args.artist[0]
bio = plot_artist_counts(artist)
bio.seek(0)

image = Image.open(bio)
image.save('./tops/play-count-for-%s.png' % slugify(artist))
bio.close()

year = 2020
bio = plot_artist_counts_for_year(artist, year)
bio.seek(0)

image = Image.open(bio)
image.save('./tops/play-count-for-%s-%d.png' % (slugify(artist), year))
bio.close()
