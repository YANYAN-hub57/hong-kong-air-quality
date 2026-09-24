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


# --------------------------------------------------
# 1. Read and parse PM2.5 data
# --------------------------------------------------

def load_pm25_data(path):
    """Read the raw AQHI XML file and return PM2.5 measurements."""

    tree = ET.parse(path)
    root = tree.getroot()

    records = []

    for item in root.iter("PollutantConcentration"):
        station = item.findtext("StationName")
        datetime_text = item.findtext("DateTime")
        pm25_text = item.findtext("PM2.5")

        if not station or not datetime_text:
            continue

        time = datetime.strptime(
            datetime_text,
            "%a, %d %b %Y %H:%M:%S %z"
        )

        # Keep missing measurements as None
        if not pm25_text or pm25_text.strip() == "-":
            pm25 = None
        else:
            pm25 = float(pm25_text)

        records.append((station, time, pm25))

    return records


records = load_pm25_data(DATA)


# --------------------------------------------------
# 3. Find all stations and times
# --------------------------------------------------

stations = sorted(set(record[0] for record in records))
times = sorted(set(record[1] for record in records))

print("Number of stations:", len(stations))
print("Number of times:", len(times))


# --------------------------------------------------
# 4. Build the matrix
# --------------------------------------------------

matrix = []

for station in stations:

    row = []

    for time in times:

        value = None

        for record_station, record_time, pm25 in records:

            if record_station == station and record_time == time:
                value = pm25
                break

        row.append(value)

    matrix.append(row)


# Matplotlib needs missing values as NaN
matrix_for_plot = [
    [
        float("nan") if value is None else value
        for value in row
    ]
    for row in matrix
]


# --------------------------------------------------
# 5. Draw heatmap
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(14, 8))

cmap = plt.colormaps["YlOrRd"].copy()
cmap.set_bad("#e6e6e6")

image = ax.imshow(
    matrix_for_plot,
    aspect="auto",
    interpolation="nearest",
    cmap=cmap
)


# --------------------------------------------------
# 6. Labels
# --------------------------------------------------

ax.set_yticks(range(len(stations)))
ax.set_yticklabels(stations)

# Show every 3rd time label
tick_positions = list(range(0, len(times), 3))

ax.set_xticks(tick_positions)

ax.set_xticklabels(
    [times[i].strftime("%d %b\n%H:%M") for i in tick_positions]
)

ax.set_title(
    "Hong Kong PM2.5 — Past 24 Hours",
    fontsize=20,
    loc="left",
    pad=28
)

ax.text(
    0,
    1.02,
    "Hourly PM2.5 concentration across 18 air-quality monitoring stations",
    transform=ax.transAxes,
    fontsize=11
)

ax.set_xlabel("Time")
ax.set_ylabel("Air Quality Monitoring Station")


# --------------------------------------------------
# 7. Colour scale
# --------------------------------------------------

colorbar = fig.colorbar(image, ax=ax)

colorbar.set_label(
    "PM2.5 concentration (µg/m³)"
)
ax.text(
    1,
    -0.12,
    "Grey = missing data  |  Source: Hong Kong Environmental Protection Department",
    transform=ax.transAxes,
    ha="right",
    fontsize=9
)

# --------------------------------------------------
# 8. Save
# --------------------------------------------------

fig.tight_layout()

OUT.parent.mkdir(exist_ok=True)

plt.savefig(
    OUT,
    dpi=180,
    bbox_inches="tight"
)

print("Saved:", OUT)

plt.show()