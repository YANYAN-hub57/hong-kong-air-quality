# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt


HERE = Path(__file__).parent
DATA = HERE / "data" / "hong-kong-air-quality-24h.xml"
OUT = HERE / "out" / "plot.png"

STATION = "Central/Western"


# Read the XML file
tree = ET.parse(DATA)
root = tree.getroot()

times = []
pm25_values = []


# Find every air-quality measurement
for item in root.iter("PollutantConcentration"):

    station = item.findtext("StationName")
    datetime_text = item.findtext("DateTime")
    pm25_text = item.findtext("PM2.5")

    # Only use Central/Western station
    if station != STATION:
        continue

    # Skip missing PM2.5 values
    if not pm25_text or pm25_text.strip() == "-":
        continue

    # Turn text into real Python values
    time = datetime.strptime(
        datetime_text,
        "%a, %d %b %Y %H:%M:%S %z"
    )

    pm25 = float(pm25_text)

    times.append(time)
    pm25_values.append(pm25)


print("Station:", STATION)
print("Number of valid measurements:", len(pm25_values))
print("First time:", times[0])
print("First PM2.5 value:", pm25_values[0])
print("PM2.5 type:", type(pm25_values[0]))


# Make the picture
fig, ax = plt.subplots(figsize=(11, 6))

ax.plot(
    times,
    pm25_values,
    marker="o"
)

ax.set_title("Hong Kong PM2.5 — Past 24 Hours")
ax.set_xlabel("Time")
ax.set_ylabel("PM2.5 concentration (µg/m³)")

ax.grid(alpha=0.25)

fig.autofmt_xdate()
fig.tight_layout()


# Save the picture
OUT.parent.mkdir(exist_ok=True)
plt.savefig(OUT, dpi=150)

print("Saved:", OUT)

plt.show()