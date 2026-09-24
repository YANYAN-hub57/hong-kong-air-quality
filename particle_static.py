# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "numpy"]
# ///

from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


HERE = Path(__file__).parent
DATA = HERE / "data" / "hong-kong-air-quality-24h.xml"
OUT = HERE / "out" / "particle-field.png"


# --------------------------------------------------
# 1. READ REAL PM2.5 DATA
# --------------------------------------------------

def load_pm25_data(path):
    """Read PM2.5 measurements from the committed AQHI XML file."""

    tree = ET.parse(path)
    root = tree.getroot()

    records = []

    for item in root.findall(".//PollutantConcentration"):
        station = item.findtext("StationName")
        time_text = item.findtext("DateTime")
        pm25_text = item.findtext("PM2.5")

        if not station or not time_text:
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

        records.append(
            {
                "station": station,
                "time": time,
                "pm25": pm25,
            }
        )

    return records


records = load_pm25_data(DATA)

stations = sorted({r["station"] for r in records})
times = sorted({r["time"] for r in records})

print("Stations:", len(stations))
print("Times:", len(times))


# --------------------------------------------------
# 2. CREATE STATION × TIME MATRIX
# --------------------------------------------------

matrix = np.full(
    (len(stations), len(times)),
    np.nan,
)

station_index = {
    station: i
    for i, station in enumerate(stations)
}

time_index = {
    time: i
    for i, time in enumerate(times)
}

for record in records:
    if record["pm25"] is None:
        continue

    i = station_index[record["station"]]
    j = time_index[record["time"]]

    matrix[i, j] = record["pm25"]


valid = matrix[np.isfinite(matrix)]

if len(valid) == 0:
    raise RuntimeError("No valid PM2.5 measurements found.")


print("Minimum PM2.5:", round(np.nanmin(matrix), 1))
print("Maximum PM2.5:", round(np.nanmax(matrix), 1))
print("Average PM2.5:", round(np.nanmean(matrix), 1))


# --------------------------------------------------
# 3. ONE HONG KONG VALUE FOR EACH HOUR
# --------------------------------------------------

# Median is used instead of mean so that one unusually high
# station does not dominate the overall hourly form.

hourly_pm25 = np.nanmedian(matrix, axis=0)

valid_hourly = hourly_pm25[np.isfinite(hourly_pm25)]

hour_min = np.nanmin(valid_hourly)
hour_max = np.nanmax(valid_hourly)

hourly_normalized = (
    (hourly_pm25 - hour_min)
    / max(hour_max - hour_min, 1e-9)
)

# Replace a missing hourly aggregate only for drawing continuity.
# The original station measurements remain untouched.
hourly_normalized = np.nan_to_num(
    hourly_normalized,
    nan=0.0,
)


# --------------------------------------------------
# 4. CREATE A SMOOTH 24-HOUR CURVE
# --------------------------------------------------

hours = np.arange(len(times))

smooth_x = np.linspace(
    0,
    len(times) - 1,
    900,
)

smooth_pm25 = np.interp(
    smooth_x,
    hours,
    hourly_normalized,
)

# Data controls vertical displacement.
# Centre around zero so the form flows above and below
# the visual centre line.
smooth_y = (
    smooth_pm25 - np.nanmean(hourly_normalized)
) * 1.35

# Add only a very small wave for visual continuity.
# The measured PM2.5 remains the dominant displacement.
smooth_y += 0.07 * np.sin(smooth_x * 0.9)


# --------------------------------------------------
# 5. COLOUR SYSTEM
# --------------------------------------------------

particle_cmap = LinearSegmentedColormap.from_list(
    "pm25_glow",
    [
        "#5877ff",
        "#7256e8",
        "#b33eae",
        "#ef416f",
        "#ff6845",
        "#ffc83d",
    ],
)


# --------------------------------------------------
# 6. CANVAS
# --------------------------------------------------

fig, ax = plt.subplots(
    figsize=(15, 7),
    facecolor="#08090f",
)

ax.set_facecolor("#08090f")

ax.set_xlim(
    -0.8,
    len(times) - 0.2,
)

ax.set_ylim(
    -2.15,
    2.15,
)

ax.axis("off")


# --------------------------------------------------
# 7. SOFT DATA-DRIVEN GLOW
# --------------------------------------------------

# Build the atmospheric glow from many translucent particles.
# PM2.5 controls both the width and strength of the glow.

rng = np.random.default_rng(42)

for x, y, value in zip(
    smooth_x,
    smooth_y,
    smooth_pm25,
):

    colour = particle_cmap(value)

    # Higher PM2.5 = broader atmospheric band.
    spread = 0.18 + value * 0.38

    # Higher PM2.5 = more visible particles.
    particle_count = int(
    5 + value * 9
    )

    px = x + rng.normal(
        0,
        0.10,
        particle_count,
    )

    py = y + rng.normal(
        0,
        spread,
        particle_count,
    )

    # Particles nearer the curve are brighter.
    distance = np.abs(py - y)

    alpha = np.clip(
        0.055
        * (1.0 - distance / (spread * 3.0))
        * (0.55 + value),
        0.008,
        0.075,
    )

    sizes = rng.uniform(
    3,
    15,
    particle_count,
    )

    ax.scatter(
        px,
        py,
        s=sizes,
        color=[colour],
        alpha=float(np.mean(alpha)),
        linewidths=0,
    )


# --------------------------------------------------
# 8. LARGE BLURRED-LIKE GLOW LAYERS
# --------------------------------------------------

# Layer translucent dots underneath the curve to create
# the soft luminous cloud seen in the visual reference.

for size, alpha in [
    (2200, 0.008),
    (1300, 0.012),
    (700, 0.018),
    (320, 0.026),
    (120, 0.035),
]:

    sample_indices = np.arange(
        0,
        len(smooth_x),
        4,
    )

    ax.scatter(
        smooth_x[sample_indices],
        smooth_y[sample_indices],
        c=smooth_pm25[sample_indices],
        cmap=particle_cmap,
        s=size,
        alpha=alpha,
        linewidths=0,
        vmin=0,
        vmax=1,
    )


# --------------------------------------------------
# 9. CENTRAL DATA CURVE
# --------------------------------------------------

# Thin dotted curve keeps the actual temporal structure visible.

ax.plot(
    smooth_x,
    smooth_y,
    color="#f2f2f2",
    linewidth=0.9,
    alpha=0.62,
    linestyle=(0, (1.5, 3.0)),
    zorder=8,
)


# --------------------------------------------------
# 10. SELECT SIX HOURS AS VISIBLE NODES
# --------------------------------------------------

node_indices = np.linspace(
    0,
    len(times) - 1,
    6,
    dtype=int,
)

node_x = node_indices

node_y = (
    hourly_normalized[node_indices]
    - np.nanmean(hourly_normalized)
) * 1.35

node_y += (
    0.07
    * np.sin(node_x * 0.9)
)


# White measurement nodes
ax.scatter(
    node_x,
    node_y,
    s=34,
    facecolor="white",
    edgecolor="#08090f",
    linewidth=1.2,
    zorder=12,
)


# --------------------------------------------------
# 11. NODE LABELS
# --------------------------------------------------

for number, index in enumerate(node_indices):

    time_label = times[index].strftime("%H:%M")

    value = hourly_pm25[index]

    # Alternate labels above and below the curve.
    if number % 2 == 0:
        offset = 0.34
        va = "bottom"
    else:
        offset = -0.34
        va = "top"

    ax.text(
        index,
        node_y[number] + offset,
        time_label,
        color="#f4f4f4",
        fontsize=10,
        ha="center",
        va=va,
        weight="medium",
        zorder=13,
    )

    ax.text(
        index,
        node_y[number] + (
            offset + 0.17
            if offset > 0
            else offset - 0.17
        ),
        f"{value:.1f} µg/m³",
        color="#92939b",
        fontsize=7.5,
        ha="center",
        va=va,
        zorder=13,
    )


# --------------------------------------------------
# 12. TITLE
# --------------------------------------------------

fig.text(
    0.075,
    0.90,
    "HONG KONG PM2.5",
    color="white",
    fontsize=25,
    weight="bold",
)

fig.text(
    0.075,
    0.855,
    "24 HOURS OF INVISIBLE AIR POLLUTION",
    color="#a0a1a8",
    fontsize=10,
)

fig.text(
    0.075,
    0.818,
    "Hourly median across Hong Kong air-quality monitoring stations",
    color="#666872",
    fontsize=8,
)


# --------------------------------------------------
# 13. LEGEND / EXPLANATION
# --------------------------------------------------

fig.text(
    0.075,
    0.105,
    "LOWER PM2.5",
    color="#7d86b9",
    fontsize=8,
)

fig.text(
    0.172,
    0.105,
    "●",
    color="#7256e8",
    fontsize=10,
)

fig.text(
    0.192,
    0.105,
    "→",
    color="#666666",
    fontsize=9,
)

fig.text(
    0.217,
    0.105,
    "●",
    color="#ef416f",
    fontsize=10,
)

fig.text(
    0.237,
    0.105,
    "→",
    color="#666666",
    fontsize=9,
)

fig.text(
    0.262,
    0.105,
    "●",
    color="#ffc83d",
    fontsize=10,
)

fig.text(
    0.285,
    0.105,
    "HIGHER PM2.5",
    color="#a39b7a",
    fontsize=8,
)


fig.text(
    0.075,
    0.068,
    "Curve = hourly median  ·  Glow width + colour = PM2.5 concentration (µg/m³)",
    color="#777982",
    fontsize=8,
)

fig.text(
    0.075,
    0.038,
    f"{len(stations)} monitoring stations  ·  {len(times)} hours  ·  "
    "Missing station measurements are not estimated",
    color="#5f6068",
    fontsize=7.5,
)

fig.text(
    0.075,
    0.016,
    "Source: Hong Kong Environmental Protection Department",
    color="#4e4f56",
    fontsize=7,
)


# --------------------------------------------------
# 14. SAVE
# --------------------------------------------------

OUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

plt.subplots_adjust(
    left=0.07,
    right=0.97,
    top=0.78,
    bottom=0.18,
)

plt.savefig(
    OUT,
    dpi=240,
    facecolor="#08090f",
    bbox_inches="tight",
    pad_inches=0.10,
)

plt.close()

print(f"Saved: {OUT}")