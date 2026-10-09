#!/usr/bin/env python
"""One-off: download + seed each dataset migrated off Socrata views export.

Run from the app container (needs Django on PYTHONPATH):

  docker exec -e PYTHONUNBUFFERED=1 -w /app app python -u scripts/test_socrata_resource_updates.py --no-seed
  sh scripts/run_socrata_smoke.sh

Full prod-like download + seed (heavy — can OOM Docker Desktop):

  docker exec -w /app app python -u scripts/test_socrata_resource_updates.py --full-download

Downloads use MEDIA_ROOT (bind-mount DATA_DIR in dev, e.g. external drive).
"""
import argparse
from unittest import mock
import os
import re
import sys
import time
import traceback
from urllib.parse import quote

# Unbuffered stdout/stderr when redirected to a log file (avoid silent logs on OOM kill).
if not os.environ.get("PYTHONUNBUFFERED"):
    os.environ["PYTHONUNBUFFERED"] = "1"
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except (AttributeError, OSError):
    pass

_APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

import django

django.setup()

from django.conf import settings

from core.utils.csv_helpers import count_csv_rows
from core.models import Dataset
from datasets import models as ds

# FK / dependency order; Property (PLUTO) is largest — last.
MODEL_NAMES = [
    # Full-table NYC Open Data /resource/ exports
    "HPDBuildingRecord",
    "HPDRegistration",
    "HPDContact",
    "AEPBuilding",
    "CONHRecord",
    "TaxLien",
    "HousingLitigation",
    "ECBViolation",
    "Eviction",
    "Property",
    # Incremental or download()-built URLs (smoke caps $limit on the final URL)
    "DOBViolation",
    "HPDComplaint",
    "HPDViolation",
    "AcrisRealMaster",
    "AcrisRealLegal",
    "AcrisRealParty",
    "DOBComplaint",
    "DOBNowFiledPermit",
    "DOBPermitIssuedNow",
    "DOBLegacyFiledPermit",
    "DOBPermitIssuedLegacy",
]

# Enough rows to catch header/format bugs without pulling full tables into memory.
DEFAULT_SMOKE_ROW_CAP = 5000

# Some models drop most CSV rows in transform (e.g. TaxLien keeps Final Sale only).
# Prefilter the Socrata export so a small $limit still yields transformed rows.
MODEL_SMOKE_WHERE = {
    "TaxLien": "lower(cycle) like '%final sale%'",
}


def apply_socrata_row_limit(url, row_cap):
    """Replace or append Socrata $limit= on resource export URLs."""
    if row_cap is None:
        return url
    if re.search(r"(\$|%24)limit=\d+", url):  # some models percent-encode the query
        return re.sub(r"(\$|%24)limit=\d+", lambda m: f"{m.group(1)}limit={row_cap}", url)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}$limit={row_cap}"


def apply_socrata_smoke_filters(model_name, url):
    where = MODEL_SMOKE_WHERE.get(model_name)
    if not where:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}$where={quote(where)}"


def count_transform_rows(model_name, path):
    model_cls = getattr(ds, model_name)
    return sum(1 for _ in model_cls.transform_self(path, update=None))


def download_dataset(model_name, row_cap=None):
    """Dataset models ignore `endpoint=` on download(); call download_file directly."""
    model_cls = getattr(ds, model_name)
    if not hasattr(model_cls, 'download_endpoint'):
        # Models that build the URL in download() (base_download_endpoint + date $where):
        # run the real download() and cap the URL it passes to download_file.
        original = model_cls.download_file

        def capped_download_file(url, *args, **kwargs):
            if row_cap is not None:
                url = apply_socrata_row_limit(url, row_cap)
            print(f"  download URL: {url}", flush=True)
            return original(url, *args, **kwargs)

        with mock.patch.object(model_cls, 'download_file', capped_download_file):
            return model_cls.download()
    url = model_cls.download_endpoint
    if row_cap is not None:
        url = apply_socrata_smoke_filters(model_name, url)
        url = apply_socrata_row_limit(url, row_cap)
    print(f"  download URL: {url}", flush=True)
    return model_cls.download_file(url)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "models",
        nargs="*",
        help="Model names to test (default: full migrated list)",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Download + transform check only (no seed_dataset / DB writes)",
    )
    parser.add_argument(
        "--keep-files",
        action="store_true",
        help="Keep downloaded CSV files on disk (default: delete after each model)",
    )
    parser.add_argument(
        "--row-cap",
        type=int,
        default=None,
        metavar="N",
        help="Socrata $limit=N per dataset (default: 5000 with --no-seed, else full table)",
    )
    parser.add_argument(
        "--full-download",
        action="store_true",
        help="Use full-table $limit (100M) even with --no-seed — can OOM; not recommended",
    )
    args = parser.parse_args()
    model_names = args.models or MODEL_NAMES

    if args.full_download:
        row_cap = None
    elif args.row_cap is not None:
        row_cap = args.row_cap
    elif args.no_seed:
        row_cap = DEFAULT_SMOKE_ROW_CAP
    else:
        row_cap = None

    print(f"MEDIA_ROOT={settings.MEDIA_ROOT}", flush=True)
    if args.no_seed:
        print("Mode: download + transform only (--no-seed)", flush=True)
    if row_cap is not None:
        print(f"Socrata row cap: {row_cap} ($limit)", flush=True)
    else:
        print("Socrata row cap: none (full table download)", flush=True)

    results = []
    for model_name in model_names:
        t0 = time.time()
        row = {
            "model": model_name,
            "download": None,
            "rows": None,
            "transform_rows": None,
            "seed": None,
            "error": None,
        }
        try:
            dataset = Dataset.objects.get(model_name=model_name)
            print(f"\n=== {dataset.name} ({model_name}) ===", flush=True)
            data_file = download_dataset(model_name, row_cap=row_cap)
            path = data_file.file.path
            row["download"] = "ok"
            row["rows"] = count_csv_rows(path) - 1  # exclude header
            print(f"  downloaded {row['rows']} rows -> {path}", flush=True)
            if row_cap is not None and row["rows"] >= row_cap:
                print(
                    f"  note: hit row cap ({row_cap}); transform check uses sample only",
                    flush=True,
                )
            row["transform_rows"] = count_transform_rows(model_name, path)
            print(f"  transform_self rows: {row['transform_rows']}", flush=True)
            if row["rows"] > 0 and row["transform_rows"] == 0:
                raise RuntimeError(
                    "transform_self produced 0 rows from a non-empty CSV "
                    "(likely column/format mismatch)"
                )
            if args.no_seed:
                row["seed"] = "skipped"
                elapsed = time.time() - t0
                print(f"  transform ok ({elapsed:.1f}s), seed skipped", flush=True)
            else:
                dataset.seed_dataset(file_path=path)
                row["seed"] = "ok"
                elapsed = time.time() - t0
                print(f"  seed ok ({elapsed:.1f}s)", flush=True)
            if args.keep_files:
                print(f"  kept file: {path}", flush=True)
            else:
                data_file.delete()
                print("  removed download file", flush=True)
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"
            print(f"  FAILED: {row['error']}", flush=True)
            traceback.print_exc()
        results.append(row)

    print("\n\n======== SUMMARY ========", flush=True)
    for r in results:
        ok = r["seed"] in ("ok", "skipped") and not r["error"]
        status = "OK" if ok else "FAIL"
        print(
            f"{status}\t{r['model']}\tdl={r['download']}\trows={r['rows']}\t"
            f"transform={r['transform_rows']}\tseed={r['seed']}\t{r['error'] or ''}",
            flush=True,
        )
    failed = [r for r in results if r["seed"] not in ("ok", "skipped") or r["error"]]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
