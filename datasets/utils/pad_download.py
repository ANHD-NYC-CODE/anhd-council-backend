"""Shared download/last-updated helpers for the NYC Open Data PAD ZIP.

Both Building and PadRecord ingest `bobaadr.txt` from the same Socrata
"download attachment" URL. This module factors the URL fetch + ZIP extract
into one place so both models stay thin.

The URL — `https://data.cityofnewyork.us/download/bc8t-ecyu/application%2Fzip` —
returns a 302 to a signed URL serving the current PAD ZIP (≈46 MB compressed,
containing bobaadr.txt at ~312 MB uncompressed). The URL is stable across PAD
releases; the file behind it changes (new ETag, new Content-Length).

bobaadr.txt is already comma-separated with quoted values — the existing CSV
import pipeline works on it once it's saved with a `.csv` extension. No format
conversion is needed.
"""

import datetime
import logging
import os
import re
import shutil
import tempfile
import zipfile

import requests
from django.core import files as dj_files

logger = logging.getLogger('app')


_SOCRATA_VIEW_ID_RE = re.compile(r'/(?:download|api/views)/([a-z0-9]{4}-[a-z0-9]{4})/?')


def _extract_socrata_view_id(url):
    """Pull `bc8t-ecyu`-style ID out of a /download/<id>/... URL."""
    m = _SOCRATA_VIEW_ID_RE.search(url or '')
    return m.group(1) if m else None


def fetch_pad_last_updated(url):
    """Use Socrata's `viewLastModified` — the real publish timestamp NYC bumps
    when they push a new quarterly PAD release. This is the date the dataset
    page shows users at
    https://data.cityofnewyork.us/City-Government/Property-Address-Directory.

    Previously this used Content-Length as a synthetic-datetime sentinel
    (mapped to seconds-since-2020). That worked but had two problems:
      1. broke if the ZIP ever shrunk (the base class compares with `>`)
      2. the api_last_updated value displayed in admin was nonsensical
         (a derived 2021 datetime that didn't match anything users could
         look up).

    viewLastModified is a real epoch timestamp from Socrata's view metadata.
    Confirmed via `/api/views/<id>.json` — bc8t-ecyu is currently
    1779824811 = 2026-05-26 (the actual NYC publish date for this release).

    Returns None on fetch failure (cron will skip this tick and retry next time,
    same behavior as the previous Content-Length implementation).
    """
    view_id = _extract_socrata_view_id(url)
    if not view_id:
        logger.warning('PAD URL has no Socrata view id: %s', url)
        return None
    try:
        resp = requests.get(
            'https://data.cityofnewyork.us/api/views/{}.json'.format(view_id),
            timeout=20,
        )
    except requests.RequestException as e:
        logger.warning('PAD viewLastModified fetch failed: %s', e)
        return None
    if resp.status_code != 200:
        logger.warning('PAD viewLastModified returned HTTP %s', resp.status_code)
        return None
    try:
        ts = int(resp.json().get('viewLastModified', 0))
    except (ValueError, TypeError, KeyError):
        return None
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)


def download_pad_bobaadr_csv(dataset, url, chunk_size=1024 * 1024):
    """Download PAD ZIP, extract bobaadr.txt, save it as bobaadr.csv DataFile.

    Streams both the HTTP download and the ZIP extraction (bobaadr.txt is ~312
    MB uncompressed; we never load the whole thing into memory). Cleans up the
    intermediate temp files in `finally` blocks even on failure.

    Returns the saved `core.models.DataFile` so the caller can pass it into the
    existing async_update_from_file pipeline.
    """
    # Avoid the circular import: pad_download is consumed by Building/PadRecord
    # which are loaded during Django app startup; importing core.models at
    # module import time would create a startup-order dependency.
    from core import models as c_models

    logger.info('Downloading PAD ZIP from %s', url)
    zip_path = None
    csv_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as zip_tmp:
            zip_path = zip_tmp.name
            with requests.get(url, stream=True, timeout=120, allow_redirects=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        zip_tmp.write(chunk)
        logger.info('PAD ZIP downloaded (%s bytes)', os.path.getsize(zip_path))

        logger.info('Extracting bobaadr.txt → bobaadr.csv (streamed)')
        with zipfile.ZipFile(zip_path) as z, \
                z.open('bobaadr.txt') as bobaadr, \
                tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as csv_tmp:
            csv_path = csv_tmp.name
            shutil.copyfileobj(bobaadr, csv_tmp, length=chunk_size)
        logger.info('bobaadr.csv ready (%s bytes)', os.path.getsize(csv_path))

        data_file = c_models.DataFile(dataset=dataset)
        with open(csv_path, 'rb') as f:
            data_file.file.save('bobaadr.csv', dj_files.File(f))
        logger.info('Saved DataFile %s at %s', data_file.id, data_file.file.path)
        return data_file
    finally:
        for path in (zip_path, csv_path):
            if path:
                try:
                    os.unlink(path)
                except OSError:
                    pass
