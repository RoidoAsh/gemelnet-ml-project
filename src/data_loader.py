"""Download and load the Gemel-Net dataset from data.gov.il.

The portal's direct CSV links block scripted downloads (HTTP 403), so the data
is pulled through the official CKAN DataStore API, page by page, and cached as
CSV files in data/raw/.
"""

### CODE ASSISTED BY CLAUDE ###
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://data.gov.il/api/3/action/datastore_search"
PAGE_SIZE = 32000

# Gemel-Net resources on data.gov.il (https://data.gov.il/he/datasets/cma/gemelnet)
RESOURCES = {
    "gemelnet_1999_2022": "91c849ed-ddc4-472b-bd09-0f5486cea35c",
    "gemelnet_2023": "2016d770-f094-4a2e-983e-797c26479720",
    "gemelnet_2024_now": "a30dcbea-a1d2-482c-ae29-8f781f5025fb",
}

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch_resource(resource_id: str) -> pd.DataFrame:
    """Fetch every row of one DataStore resource through the API."""
    records, offset, total = [], 0, None
    while total is None or offset < total:
        response = requests.get(
            API_URL,
            params={"resource_id": resource_id, "limit": PAGE_SIZE, "offset": offset},
            timeout=180,
        )
        response.raise_for_status()
        result = response.json()["result"]
        total = result["total"]
        records.extend(result["records"])
        offset += PAGE_SIZE
    return pd.DataFrame.from_records(records).drop(columns="_id")


def download_all(force: bool = False) -> dict[str, Path]:
    """Save each resource to data/raw/<name>.csv, skipping files that already exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, resource_id in RESOURCES.items():
        path = RAW_DIR / f"{name}.csv"
        if force or not path.exists():
            df = fetch_resource(resource_id)
            df.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"Downloaded {name}: {len(df):,} rows -> {path.name}")
        else:
            print(f"Already exists, skipping: {path.name}")
        paths[name] = path
    return paths


def load_raw() -> dict[str, pd.DataFrame]:
    """Load the cached raw CSVs (downloading any that are missing)."""
    return {name: pd.read_csv(path) for name, path in download_all().items()}
####


if __name__ == "__main__":
    download_all()
