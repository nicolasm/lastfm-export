#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from pathlib import Path

from PIL import Image

from plot.plot import plot_play_counts_last_n_years

logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s %(levelname)s %(message)s'
)

bio = plot_play_counts_last_n_years(5)
bio.seek(0)

Path('./tops').mkdir(parents=True, exist_ok=True)

image = Image.open(bio)
image.save('./tops/play-count-for-last-n-years.png')
bio.close()
