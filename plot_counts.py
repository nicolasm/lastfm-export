#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

from PIL import Image

from plot.plot import plot_play_counts_by_month

bio = plot_play_counts_by_month()
bio.seek(0)

Path('./tops').mkdir(parents=True, exist_ok=True)

image = Image.open(bio)
image.save('./tops/play-count-by-month.png')
bio.close()
