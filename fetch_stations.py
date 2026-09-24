# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""
Download the official Hong Kong Air Quality Monitoring Network
geographic data once and save it locally as GeoJSON.

Source:
Hong Kong Environmental Protection Department
Common Spatial Data Infrastructure (CSDI)
"""

from pathlib import Path
import json
import requests


HERE = Path(__file__).parent
DATA = HERE / "data"

DATASET_ID = "epd_rcd_1629267205214_40635"

LAYER_URL = (
    "https://portal.csdi.gov.hk/server/rest/services/common/"
    f"{DATASET_ID}/FeatureServer/0"
)

OUT = DATA / "monitoring-stations.geojson"


def get_json(url, params=None):
    """Request JSON from the official CSDI service."""

    response = requests.get(
        url,
        params=params,
        timeout=60,
        headers={
            "User-Agent": "SD5913 PolyU student"
        },
    )

    response.raise_for_status()

    return response.json()


def download_stations():
    """Download official monitoring-station locations as GeoJSON."""

    DATA.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("Hong Kong Air Quality Monitoring Network")
    print("----------------------------------------")
    print("Official layer: AQMN")
    print()

    query_url = f"{LAYER_URL}/query"

    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }

    print("Downloading official station geography...")

    data = get_json(
        query_url,
        params,
    )

    features = data.get("features", [])

    print("Features downloaded:", len(features))

    if not features:
        raise RuntimeError(
            "The official service returned no station features."
        )

    OUT.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Saved: {OUT}")
    print()

    # Inspect the first feature so we can see
    # the official property names.
    first = features[0]

    print("First feature properties:")
    print(
        json.dumps(
            first.get("properties", {}),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("First feature coordinates:")
    print(
        first.get("geometry", {}).get("coordinates")
    )


if __name__ == "__main__":
    download_stations()