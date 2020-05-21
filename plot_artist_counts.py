#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

from PIL import Image

from plot.plot import plot_artist_counts, plot_artist_counts_for_year

Path('./tops').mkdir(parents=True, exist_ok=True)

bio = plot_artist_counts('Emily Bezar')
bio.seek(0)

image = Image.open(bio)
image.save('./tops/play-count-for-emily-bezar.png')
bio.close()

bio = plot_artist_counts_for_year('Emily Bezar', 2019)
bio.seek(0)

image = Image.open(bio)
image.save('./tops/play-count-for-emily-bezar-2019.png')
bio.close()
