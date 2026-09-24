# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
import json


HERE = Path(__file__).parent

PM25_FILE = (
    HERE / "data" / "hong-kong-air-quality-24h.xml"
)

STATION_FILE = (
    HERE / "data" / "monitoring-stations.geojson"
)

OUTPUT_FILE = (
    HERE / "site" / "pm25-map-data.json"
)


# --------------------------------------------------
# 1. NORMALISE STATION NAME
# --------------------------------------------------

def clean_geo_name(full_name):
    """Convert official CSDI station name to AQHI short name."""

    return (
        full_name
        .replace(
            " Air Quality Monitoring Station",
            "",
        )
        .strip()
    )


# --------------------------------------------------
# 2. READ OFFICIAL STATION LOCATIONS
# --------------------------------------------------

with open(
    STATION_FILE,
    "r",
    encoding="utf-8",
) as file:
    geojson = json.load(file)


locations = {}


for feature in geojson["features"]:

    properties = feature["properties"]

    name = clean_geo_name(
        properties["NAME_EN"]
    )

    longitude, latitude = (
        feature["geometry"]["coordinates"][:2]
    )

    locations[name] = {
        "latitude": latitude,
        "longitude": longitude,
        "type": properties.get(
            "SEARCH01_EN",
            "UNKNOWN",
        ),
    }


# --------------------------------------------------
# 3. READ PM2.5 XML
# --------------------------------------------------

tree = ET.parse(PM25_FILE)
root = tree.getroot()

records = []


for item in root.findall(
    ".//PollutantConcentration"
):

    station = item.findtext(
        "StationName"
    )

    time_text = item.findtext(
        "DateTime"
    )

    pm25_text = item.findtext(
        "PM2.5"
    )

    if not station or not time_text:
        continue

    station = station.strip()

    if station not in locations:
        continue

    try:
        time = datetime.strptime(
            time_text,
            "%a, %d %b %Y %H:%M:%S %z",
        )
    except ValueError:
        continue

    try:
        pm25 = float(pm25_text)
    except (TypeError, ValueError):
        pm25 = None

    location = locations[station]

    records.append(
        {
            "station": station,
            "time": time.isoformat(),
            "hour": time.strftime("%H:%M"),
            "pm25": pm25,
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "type": location["type"],
        }
    )


# --------------------------------------------------
# 4. BUILD OUTPUT
# --------------------------------------------------

times = sorted({
    record["time"]
    for record in records
})


stations = sorted({
    record["station"]
    for record in records
})


output = {
    "title": "Hong Kong PM2.5",
    "unit": "µg/m³",
    "source": (
        "Hong Kong Environmental "
        "Protection Department"
    ),
    "station_count": len(stations),
    "time_count": len(times),
    "times": times,
    "records": records,
}


# --------------------------------------------------
# 5. SAVE
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


OUTPUT_FILE.write_text(
    json.dumps(
        output,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)


print()
print("HONG KONG PM2.5 — MAP DATA")
print("=" * 50)

print(
    "Stations:",
    len(stations),
)

print(
    "Times:",
    len(times),
)

print(
    "Records:",
    len(records),
)

print()

print(
    "Saved:",
    OUTPUT_FILE,
)
