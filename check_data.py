from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).parent
FILE = HERE / "data" / "hong-kong-air-quality-24h.xml"

tree = ET.parse(FILE)
root = tree.getroot()

print("Root:", root.tag)

count = 0

for item in root.iter("PollutantConcentration"):
    station = item.findtext("StationName")
    datetime = item.findtext("DateTime")
    pm25 = item.findtext("PM2.5")

    print("Station:", station)
    print("DateTime:", datetime)
    print("PM2.5:", repr(pm25))
    print("--------------------")

    count += 1

    if count == 10:
        break