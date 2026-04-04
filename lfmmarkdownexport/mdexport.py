"""
lfmmarkdownexport/mdexport.py

Low-level helpers for writing Last.fm tops to Markdown with embedded images.
"""

import base64
from io import BytesIO


def bio_to_base64(bio: BytesIO) -> str:
    """Convert a BytesIO PNG image to a base64 data URI."""
    bio.seek(0)
    return base64.b64encode(bio.read()).decode('utf-8')


def md_image(alt: str, bio: BytesIO) -> str:
    """Return a Markdown image tag with embedded base64 PNG."""
    return "![%s](data:image/png;base64,%s)" % (alt, bio_to_base64(bio))


def md_table(headers: list, rows: list) -> str:
    """
    Return a Markdown table string.

    Parameters
    ----------
    headers : list of str
    rows    : list of tuples
    """
    lines = []
    lines.append("| # | " + " | ".join(headers) + " |")
    lines.append("|---|" + "---|" * len(headers))
    for i, row in enumerate(rows, start=1):
        lines.append("| %d | " % i + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def md_section(title: str, table: str, image: str) -> str:
    """Return a Markdown section with a heading, table and image."""
    return "## %s\n\n%s\n\n%s\n" % (title, table, image)
