from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).parent
FILE = HERE / "data" / "hong-kong-air-quality-24h.xml"

tree = ET.parse(FILE)
root = tree.getroot()

station_counts = {}

for item in root.iter("PollutantConcentration"):
    station = item.findtext("StationName")
    pm25 = item.findtext("PM2.5")

    if not station:
        continue

    if station not in station_counts:
        station_counts[station] = 0

    if pm25 and pm25.strip() != "-":
        station_counts[station] += 1

print("Valid PM2.5 measurements by station:")
print()

for station in sorted(station_counts):
    print(f"{station:20} {station_counts[station]}")