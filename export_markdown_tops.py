#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_markdown_tops.py

Generates one Markdown file per time period with tops tables and embedded
matplotlib bar charts:
  - tops/last-7-days.md
  - tops/last-30-days.md
  - tops/last-90-days.md
  - tops/last-180-days.md
  - tops/last-365-days.md
  - tops/all-time.md
  - tops/2006.md ... tops/YYYY.md

Usage:
    python export_markdown_tops.py
"""

from datetime import datetime
from pathlib import Path

from lfmconf.lfmconf import get_lastfm_conf
from lfmmarkdownexport.mdexport import md_image, md_table, md_section
from lfmpandas.lfmpandas import (
    AggregationType,
    DataFrameColumn,
    retrieve_top_artists_for_duration_as_dataframe,
    retrieve_top_artists_for_year_as_dataframe,
    retrieve_top_albums_for_duration_as_dataframe,
    retrieve_top_albums_for_year_as_dataframe,
    retrieve_top_tracks_for_duration_as_dataframe,
    retrieve_top_tracks_for_year_as_dataframe,
)
from plot.plot import plot_top
from plottop.plotop import Duration, Year, PlotType

conf       = get_lastfm_conf()
START_YEAR = conf['lastfm']['service']['startYear']
LIMIT      = conf.get('excelExport', {}).get('limit', 20)
OUTPUT_DIR = Path('tops')


# ── Data helpers ──────────────────────────────────────────────────────────────

def _artists_rows(df):
    return list(df[['Artist', 'PlayCount']].itertuples(index=False, name=None))

def _albums_rows(df):
    return list(df[['ArtistAlbum', 'PlayCount']].itertuples(index=False, name=None))

def _tracks_rows(df):
    return list(df[['ArtistAlbumTrack', 'PlayCount']].itertuples(index=False, name=None))


# ── File builder ──────────────────────────────────────────────────────────────

def _build_file(period, is_year=False):
    """
    Build a Markdown file for the given period.

    Parameters
    ----------
    period  : Duration or Year instance
    is_year : bool
    """
    period_value = period.get_value()
    label        = period.get_label()

    if is_year:
        df_artists = retrieve_top_artists_for_year_as_dataframe(period_value, LIMIT, False)
        df_albums  = retrieve_top_albums_for_year_as_dataframe(period_value, LIMIT, False)
        df_tracks  = retrieve_top_tracks_for_year_as_dataframe(period_value, LIMIT, False)
        agg_artists = AggregationType.YearArtist
        agg_albums  = AggregationType.YearAlbum
        agg_tracks  = AggregationType.YearTrack
    else:
        df_artists = retrieve_top_artists_for_duration_as_dataframe(period_value, LIMIT, False)
        df_albums  = retrieve_top_albums_for_duration_as_dataframe(period_value, LIMIT, False)
        df_tracks  = retrieve_top_tracks_for_duration_as_dataframe(period_value, LIMIT, False)
        agg_artists = AggregationType.DurationArtist
        agg_albums  = AggregationType.DurationAlbum
        agg_tracks  = AggregationType.DurationTrack

    lines = ["# Top — %s\n" % label]

    # ── Top Artists ──
    bio_artists = plot_top(period, agg_artists, PlotType.BarH,
                           DataFrameColumn.Artist, False)
    lines.append(md_section(
        "Top Artists",
        md_table(["Artist", "Plays"], _artists_rows(df_artists)),
        md_image("Top Artists", bio_artists),
    ))

    # ── Top Albums ──
    bio_albums = plot_top(period, agg_albums, PlotType.BarH,
                          DataFrameColumn.ArtistAlbum, False)
    lines.append(md_section(
        "Top Albums",
        md_table(["Album", "Plays"], _albums_rows(df_albums)),
        md_image("Top Albums", bio_albums),
    ))

    # ── Top Tracks ──
    bio_tracks = plot_top(period, agg_tracks, PlotType.BarH,
                          DataFrameColumn.ArtistAlbumTrack, False)
    lines.append(md_section(
        "Top Tracks",
        md_table(["Track", "Plays"], _tracks_rows(df_tracks)),
        md_image("Top Tracks", bio_tracks),
    ))

    output_path = OUTPUT_DIR / ("%s.md" % label)
    output_path.write_text("\n".join(lines), encoding='utf-8')
    print("  ✓ %s" % output_path)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Exporting Markdown tops by duration...")
    for duration in [
        Duration.WEEK,
        Duration.MONTH,
        Duration.QUARTER,
        Duration.SEMESTER,
        Duration.YEAR,
        Duration.OVERALL,
    ]:
        _build_file(duration, is_year=False)

    print("\nExporting Markdown tops by year...")
    now = datetime.now()
    for year in reversed(range(START_YEAR, now.year + 1)):
        _build_file(Year(year), is_year=True)

    print("\nDone.")
