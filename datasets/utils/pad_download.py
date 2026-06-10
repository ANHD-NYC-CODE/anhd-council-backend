"""Shared download/last-updated helpers for the NYC Open Data PAD ZIP.

Both Building and PadRecord ingest `bobaadr.txt` from the same Socrata
"download attachment" URL. This module factors the URL fetch + ZIP extract
into one place so both models stay thin.

The URL — `https://data.cityofnewyork.us/download/bc8t-ecyu/application%2Fzip` —
returns a 302 to a signed URL serving the current PAD ZIP (≈46 MB compressed,
containing bobaadr.txt at ~312 MB uncompressed). The URL is stable across PAD
releases; the file behind it changes, and its ETag (the Socrata file UUID)
along with its Content-Length both change.

bobaadr.txt is already comma-separated with quoted values — the existing CSV
import pipeline works on it once it's saved with a `.csv` extension. No format
conversion is needed.
"""

import datetime
import logging
import os
import shutil
import tempfile
import zipfile

import requests
from django.core import files as dj_files

logger = logging.getLogger('app')


def fetch_pad_last_updated(url):
    """Synthetic 'last updated' derived from the ZIP's Content-Length.

    Why this works as a release sentinel:
    - HEAD on the PAD download URL returns Content-Length but no Last-Modified.
    - New PAD releases add buildings, so the ZIP grows; Content-Length increases
      with each quarterly release.
    - The base check (`check_api_for_update_and_update`) compares this against
      the stored `api_last_updated` with `>`. Mapping size → seconds-since-2020
      keeps the comparison monotonic with size.

    Returns None on HEAD failure (the cron will then skip this run and retry
    on the next tick — same behavior as other automated datasets when the
    upstream is unreachable).
    """
    try:
        resp = requests.head(url, allow_redirects=True, timeout=20)
    except requests.RequestException as e:
        logger.warning('PAD HEAD failed: %s', e)
        return None
    if resp.status_code != 200:
        logger.warning('PAD HEAD returned HTTP %s', resp.status_code)
        return None
    try:
        size = int(resp.headers.get('content-length', '0'))
    except ValueError:
        return None
    if not size:
        return None
    return datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=size)


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
