#!/usr/bin/env python
"""One-off: download + seed each dataset migrated off Socrata views export.

Run from the app container (needs Django on PYTHONPATH):

  docker exec -w /app app python manage.py shell < scripts/test_socrata_resource_updates.py

Or: docker exec -w /app app python scripts/test_socrata_resource_updates.py
only works if cwd is /app and DJANGO_SETTINGS_MODULE is set (see docker-entrypoint).
"""
import os
import sys
import time
import traceback

# Allow `python scripts/...` when launched from /app in Docker (same as manage.py).
_APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

import django

django.setup()

from core.utils.csv_helpers import count_csv_rows
from core.models import Dataset

# FK / dependency order; Property (PLUTO) is largest — last.
MODEL_NAMES = [
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
]


def main():
    results = []
    for model_name in MODEL_NAMES:
        t0 = time.time()
        row = {"model": model_name, "download": None, "rows": None, "seed": None, "error": None}
        try:
            dataset = Dataset.objects.get(model_name=model_name)
            print(f"\n=== {dataset.name} ({model_name}) ===", flush=True)
            data_file = dataset.download()
            path = data_file.file.path
            row["download"] = "ok"
            row["rows"] = count_csv_rows(path) - 1  # exclude header
            print(f"  downloaded {row['rows']} rows -> {path}", flush=True)
            dataset.seed_dataset(file_path=path)
            row["seed"] = "ok"
            # Local test only — prod seed_dataset still keeps files (delete_old_files).
            data_file.delete()
            elapsed = time.time() - t0
            print(f"  seed ok ({elapsed:.1f}s), removed download file", flush=True)
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"
            print(f"  FAILED: {row['error']}", flush=True)
            traceback.print_exc()
        results.append(row)

    print("\n\n======== SUMMARY ========", flush=True)
    for r in results:
        status = "OK" if r["seed"] == "ok" else "FAIL"
        print(
            f"{status}\t{r['model']}\tdl={r['download']}\trows={r['rows']}\tseed={r['seed']}\t{r['error'] or ''}",
            flush=True,
        )
    failed = [r for r in results if r["seed"] != "ok"]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
