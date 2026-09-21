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

tree = ET.parse(DATA)
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


stations = sorted({r["station"] for r in records})
times = sorted({r["time"] for r in records})

print("Stations:", len(stations))
print("Times:", len(times))


# --------------------------------------------------
# 2. CREATE 18 × 24 DATA MATRIX
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


minimum = np.nanmin(matrix)
maximum = np.nanmax(matrix)
mean = np.nanmean(matrix)

print("Minimum PM2.5:", round(minimum, 1))
print("Maximum PM2.5:", round(maximum, 1))
print("Average PM2.5:", round(mean, 1))


normalized = (
    (matrix - minimum)
    / max(maximum - minimum, 1e-9)
)


# --------------------------------------------------
# 3. PARTICLE GRID
# --------------------------------------------------

ROWS = 125
COLS = 165

u = np.linspace(-np.pi, np.pi, COLS)
v = np.linspace(-np.pi, np.pi, ROWS)

U, V = np.meshgrid(u, v)


# --------------------------------------------------
# 4. BASE ORGANIC FORM
# --------------------------------------------------

radius = (
    2.35
    + 0.30 * np.sin(3 * U)
    + 0.22 * np.cos(4 * V)
    + 0.18 * np.sin(2 * U + 3 * V)
    + 0.12 * np.cos(5 * U - V)
)


# --------------------------------------------------
# 5. LET REAL PM2.5 DATA DEFORM THE FORM
# --------------------------------------------------

for i in range(len(stations)):

    for j in range(len(times)):

        value = normalized[i, j]

        if not np.isfinite(value):
            continue

        data_u = (
            j / max(len(times) - 1, 1)
        ) * 2 * np.pi - np.pi

        data_v = (
            i / max(len(stations) - 1, 1)
        ) * 2 * np.pi - np.pi

        distance = (
            (U - data_u) ** 2
            + (V - data_v) ** 2
        )

        influence = np.exp(
            -distance / 0.20
        )

        radius += (
            influence
            * value
            * 0.55
        )


# --------------------------------------------------
# 6. CONVERT SURFACE INTO 3D PARTICLES
# --------------------------------------------------

X = (
    radius
    * np.cos(V)
    * np.cos(U)
)

Y = (
    radius
    * np.cos(V)
    * np.sin(U)
)

Z = (
    radius
    * np.sin(V)
)


# Add a flowing deformation

X += 0.28 * np.sin(V * 3 + U)
Y += 0.22 * np.cos(U * 2 - V)
Z += 0.30 * np.sin(U * 2 + V * 2)


# --------------------------------------------------
# 7. PARTICLE COLOUR
# --------------------------------------------------

colour = (
    0.45
    + 0.30 * np.sin(U * 1.3)
    + 0.20 * np.cos(V * 1.8)
    + 0.18 * Z
)

colour = (
    colour - colour.min()
) / (
    colour.max() - colour.min()
)


# Custom palette inspired by the reference image

particle_cmap = LinearSegmentedColormap.from_list(
    "particle",
    [
        "#31105c",
        "#602080",
        "#9c2f73",
        "#d74652",
        "#ff7138",
        "#ffad32",
    ],
)


# --------------------------------------------------
# 8. DRAW
# --------------------------------------------------

fig = plt.figure(
    figsize=(10, 10),
    facecolor="#000000",
)

ax = fig.add_subplot(
    111,
    projection="3d",
)

ax.set_facecolor("#000000")


particles = ax.scatter(
    X.flatten(),
    Y.flatten(),
    Z.flatten(),
    c=colour.flatten(),
    cmap=particle_cmap,
    s=3.6,
    alpha=0.96,
    linewidths=0,
    depthshade=False,
)


# --------------------------------------------------
# 9. CAMERA
# --------------------------------------------------

ax.view_init(
    elev=18,
    azim=-48,
)

ax.set_box_aspect(
    (1, 1, 1)
)

ax.set_xlim(-3.6, 3.6)
ax.set_ylim(-3.6, 3.6)
ax.set_zlim(-3.6, 3.6)

ax.set_axis_off()


# Make the artwork occupy most of the image

ax.set_position(
    [0.06, 0.08, 0.88, 0.82]
)


# --------------------------------------------------
# 10. TYPOGRAPHY
# --------------------------------------------------

fig.text(
    0.07,
    0.94,
    "HONG KONG PM2.5",
    color="white",
    fontsize=24,
    weight="bold",
)

fig.text(
    0.07,
    0.905,
    "PAST 24 HOURS · PARTICLE FIELD",
    color="#999999",
    fontsize=10,
)


fig.text(
    0.07,
    0.060,
    "18 monitoring stations  ·  24 hours",
    color="#999999",
    fontsize=9,
)

fig.text(
    0.07,
    0.038,
    "Particle displacement is influenced by measured PM2.5 concentration",
    color="#777777",
    fontsize=8,
)

fig.text(
    0.07,
    0.018,
    "Source: Hong Kong Environmental Protection Department",
    color="#555555",
    fontsize=7,
)


# --------------------------------------------------
# 11. SAVE
# --------------------------------------------------

OUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

plt.savefig(
    OUT,
    dpi=240,
    facecolor="#000000",
    bbox_inches="tight",
    pad_inches=0.08,
)

plt.close()

print(f"Saved: {OUT}")