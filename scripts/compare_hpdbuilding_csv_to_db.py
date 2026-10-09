#!/usr/bin/env python
"""Compare on-disk HPD Building CSV to DB — estimates impact of switching to full upsert.

Usage (prod, uses latest DataFile or a path):
  docker exec -w /app app python scripts/compare_hpdbuilding_csv_to_db.py
  docker exec -w /app app python scripts/compare_hpdbuilding_csv_to_db.py /app/data/file.csv
"""
import os
import sys

_APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.production")

import django

django.setup()

import csv
from collections import Counter, defaultdict

from core.models import DataFile
from core.utils.transform import clean_headers
from datasets.models import HPDBuildingRecord

PA_FIELDS = ("legalclassa", "legalclassb", "managementprogram")
OTHER_FIELDS = (
    "housenumber",
    "streetname",
    "lifecycle",
    "recordstatus",
    "registrationid_id",
    "zip",
)
ALL_FIELDS = PA_FIELDS + OTHER_FIELDS


def norm(value):
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() == "null":
        return None
    return s


def norm_int(value):
    n = norm(value)
    if n is None:
        return None
    try:
        return int(float(n))
    except (TypeError, ValueError):
        return n


def csv_path_from_argv():
    if len(sys.argv) > 1:
        return sys.argv[1]
    f = (
        DataFile.objects.filter(dataset__model_name="HPDBuildingRecord")
        .order_by("-id")
        .first()
    )
    if not f or not f.file:
        raise SystemExit("No HPD Building DataFile found; pass a CSV path.")
    return f.file.path


def main():
    path = csv_path_from_argv()
    print(f"CSV: {path}", flush=True)

    db_rows = {
        str(r["buildingid"]): r
        for r in HPDBuildingRecord.objects.values(
            "buildingid",
            "bbl_id",
            *ALL_FIELDS,
        )
    }
    print(f"DB rows: {len(db_rows)}", flush=True)

    csv_ids = set()
    new_in_csv = 0
    unchanged = 0
    changed_rows = 0
    field_hits = Counter()
    pa_affected_bbls = set()

    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        headers = clean_headers(fh.readline())
        reader = csv.DictReader(fh, fieldnames=headers)
        for row in reader:
            bid = norm(row.get("buildingid"))
            if not bid:
                continue
            csv_ids.add(bid)
            db = db_rows.get(bid)
            if db is None:
                new_in_csv += 1
                continue

            row_changed = False
            pa_changed = False
            for field in ALL_FIELDS:
                csv_key = "registrationid" if field == "registrationid_id" else field
                csv_val = row.get(csv_key)
                db_val = db[field]
                if field in ("legalclassa", "legalclassb", "registrationid"):
                    equal = norm_int(csv_val) == norm_int(db_val)
                else:
                    equal = norm(csv_val) == norm(db_val)
                if not equal:
                    field_hits[field] += 1
                    row_changed = True
                    if field in PA_FIELDS:
                        pa_changed = True
            if row_changed:
                changed_rows += 1
                if pa_changed and db["bbl_id"]:
                    pa_affected_bbls.add(db["bbl_id"])
            else:
                unchanged += 1

    ghosts_in_db = len(db_rows) - len(csv_ids & set(db_rows.keys()))

    print("\n=== Row-level (CSV vs DB, same buildingid) ===", flush=True)
    print(f"  CSV rows (with buildingid): {len(csv_ids)}", flush=True)
    print(f"  New buildingid in CSV only (would INSERT): {new_in_csv}", flush=True)
    print(f"  Unchanged on compared fields: {unchanged}", flush=True)
    print(f"  Would UPDATE (≥1 field differs): {changed_rows}", flush=True)
    print(f"  DB buildingids not in this CSV (ghosts): {ghosts_in_db}", flush=True)

    print("\n=== Field mismatch counts (among would-UPDATE rows) ===", flush=True)
    for field, count in field_hits.most_common():
        tag = " [PA]" if field in PA_FIELDS else ""
        print(f"  {field}{tag}: {count}", flush=True)

    print("\n=== PropertyAnnotation impact (estimate) ===", flush=True)
    print(
        f"  Distinct BBLs where PA fields would change after upsert+annotate: {len(pa_affected_bbls)}",
        flush=True,
    )

    # Sample a few PA-impacting diffs
    samples = []
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        headers = clean_headers(fh.readline())
        reader = csv.DictReader(fh, fieldnames=headers)
        for row in reader:
            bid = norm(row.get("buildingid"))
            db = db_rows.get(bid) if bid else None
            if not db or not db["bbl_id"]:
                continue
            for field in PA_FIELDS:
                if field in ("legalclassa", "legalclassb"):
                    eq = norm_int(row.get(field)) == norm_int(db[field])
                else:
                    eq = norm(row.get(field)) == norm(db[field])
                if not eq:
                    samples.append(
                        (bid, db["bbl_id"], field, db[field], row.get(field))
                    )
                    break
            if len(samples) >= 8:
                break

    if samples:
        print("\n=== Sample PA field diffs (db → csv) ===", flush=True)
        for bid, bbl, field, old, new in samples:
            print(f"  buildingid={bid} bbl={bbl} {field}: {old!r} → {new!r}", flush=True)


if __name__ == "__main__":
    main()
