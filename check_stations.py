# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from pathlib import Path
import json
import xml.etree.ElementTree as ET


HERE = Path(__file__).parent

PM25_FILE = (
    HERE
    / "data"
    / "hong-kong-air-quality-24h.xml"
)

STATION_FILE = (
    HERE
    / "data"
    / "monitoring-stations.geojson"
)


# --------------------------------------------------
# 1. READ STATION NAMES FROM PM2.5 XML
# --------------------------------------------------

tree = ET.parse(PM25_FILE)
root = tree.getroot()

xml_stations = sorted({
    item.findtext("StationName").strip()
    for item in root.findall(".//PollutantConcentration")
    if item.findtext("StationName")
})


# --------------------------------------------------
# 2. READ OFFICIAL GEOGRAPHIC STATIONS
# --------------------------------------------------

with open(
    STATION_FILE,
    "r",
    encoding="utf-8",
) as file:
    geojson = json.load(file)


geo_stations = {}

for feature in geojson["features"]:

    properties = feature["properties"]

    full_name = properties["NAME_EN"]

    # Example:
    # "Tsuen Wan Air Quality Monitoring Station"
    #
    # becomes:
    # "Tsuen Wan"

    short_name = full_name.replace(
        " Air Quality Monitoring Station",
        "",
    ).strip()

    coordinates = feature["geometry"]["coordinates"]

    longitude = coordinates[0]
    latitude = coordinates[1]

    station_type = properties.get(
        "SEARCH01_EN",
        "UNKNOWN",
    )

    geo_stations[short_name] = {
        "longitude": longitude,
        "latitude": latitude,
        "type": station_type,
        "full_name": full_name,
    }


# --------------------------------------------------
# 3. SPECIAL NAME NORMALISATION
# --------------------------------------------------

def normalize_station_name(name):
    """
    Make station names comparable between the
    PM2.5 XML and official geographic dataset.
    """

    name = name.strip()

    replacements = {
        "Central/Western": "Central/Western",
    }

    return replacements.get(
        name,
        name,
    )


# --------------------------------------------------
# 4. MATCH BOTH DATASETS
# --------------------------------------------------

print()
print("HONG KONG PM2.5 — STATION MATCH")
print("=" * 62)
print()

matched = []
missing = []


for station in xml_stations:

    normalized = normalize_station_name(
        station
    )

    if normalized in geo_stations:

        info = geo_stations[normalized]

        matched.append(station)

        print(
            f"✓ {station:<20}"
            f"{info['latitude']:.5f}, "
            f"{info['longitude']:.5f}"
        )

    else:

        missing.append(station)

        print(
            f"✗ {station:<20}"
            "NO GEOGRAPHIC MATCH"
        )


# --------------------------------------------------
# 5. RESULT
# --------------------------------------------------

print()
print("=" * 62)

print(
    f"Matched: {len(matched)} / "
    f"{len(xml_stations)}"
)

if missing:

    print()
    print("Stations still needing attention:")

    for station in missing:
        print(
            " -",
            station,
        )

else:

    print()
    print(
        "SUCCESS — all PM2.5 stations have "
        "official geographic coordinates."
    )