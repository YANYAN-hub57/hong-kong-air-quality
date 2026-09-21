# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "pillow"]
# ///

from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


# ------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------

HERE = Path(__file__).parent
DATA = HERE / "data" / "hong-kong-air-quality-24h.xml"
OUT = HERE / "out" / "pm25-animation.gif"


# ------------------------------------------------------------
# 2. Read XML
# ------------------------------------------------------------

tree = ET.parse(DATA)
root = tree.getroot()


# ------------------------------------------------------------
# 3. Collect PM2.5 measurements
# ------------------------------------------------------------

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

    # Keep missing measurements as None.
    if not pm25_text or pm25_text.strip() == "-":
        pm25 = None
    else:
        pm25 = float(pm25_text)

    records.append((station, time, pm25))


# ------------------------------------------------------------
# 4. Find stations and times
# ------------------------------------------------------------

stations = sorted(set(record[0] for record in records))
times = sorted(set(record[1] for record in records))

print("Number of stations:", len(stations))
print("Number of times:", len(times))


# ------------------------------------------------------------
# 5. Build station × time matrix
# ------------------------------------------------------------

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


matrix_for_plot = [
    [
        float("nan") if value is None else value
        for value in row
    ]
    for row in matrix
]


# ------------------------------------------------------------
# 6. Keep one colour scale for the whole animation
# ------------------------------------------------------------

valid_values = [
    value
    for row in matrix
    for value in row
    if value is not None
]

vmin = min(valid_values)
vmax = max(valid_values)


# ------------------------------------------------------------
# 7. Figure design
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(14, 8))

fig.patch.set_facecolor("#f7f7f5")
ax.set_facecolor("#f7f7f5")

cmap = plt.colormaps["YlOrRd"].copy()
cmap.set_bad("#d9d9d9")


# Start with only the first hour visible.
first_frame = [
    [row[0]] + [float("nan")] * (len(times) - 1)
    for row in matrix_for_plot
]

image = ax.imshow(
    first_frame,
    aspect="auto",
    interpolation="nearest",
    cmap=cmap,
    vmin=vmin,
    vmax=vmax
)


# ------------------------------------------------------------
# 8. Labels
# ------------------------------------------------------------

ax.set_yticks(range(len(stations)))
ax.set_yticklabels(stations, fontsize=9)

tick_positions = list(range(0, len(times), 3))

ax.set_xticks(tick_positions)

ax.set_xticklabels(
    [times[i].strftime("%d %b\n%H:%M") for i in tick_positions],
    fontsize=9
)

ax.set_xlabel(
    "Time",
    fontsize=10,
    labelpad=12
)

ax.set_ylabel(
    "Air Quality Monitoring Station",
    fontsize=10,
    labelpad=12
)


# Remove unnecessary frame lines.
for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(length=0)


# ------------------------------------------------------------
# 9. Title
# ------------------------------------------------------------

fig.suptitle(
    "HONG KONG PM2.5",
    x=0.125,
    y=0.96,
    ha="left",
    fontsize=24,
    fontweight="bold"
)

subtitle = ax.set_title(
    "",
    loc="left",
    fontsize=12,
    pad=25
)


# ------------------------------------------------------------
# 10. Colour scale
# ------------------------------------------------------------

colorbar = fig.colorbar(
    image,
    ax=ax,
    fraction=0.025,
    pad=0.03
)

colorbar.set_label(
    "PM2.5 concentration (µg/m³)",
    fontsize=10
)

colorbar.outline.set_visible(False)


# ------------------------------------------------------------
# 11. Footer
# ------------------------------------------------------------

fig.text(
    0.125,
    0.035,
    "Grey = missing measurement",
    fontsize=9,
    color="#666666"
)

fig.text(
    0.88,
    0.035,
    "Source: Hong Kong Environmental Protection Department · AQHI",
    fontsize=9,
    color="#666666",
    ha="right"
)


# ------------------------------------------------------------
# 12. Animation
# ------------------------------------------------------------

def update(frame):

    # Reveal one additional hour on every frame.
    visible_matrix = []

    for row in matrix_for_plot:

        visible_row = []

        for column, value in enumerate(row):

            if column <= frame:
                visible_row.append(value)
            else:
                visible_row.append(float("nan"))

        visible_matrix.append(visible_row)

    image.set_data(visible_matrix)

    current_time = times[frame]

    subtitle.set_text(
        "Past 24 Hours  ·  "
        f"Now showing {current_time.strftime('%d %b %Y · %H:%M')}"
    )

    return image, subtitle


animation = FuncAnimation(
    fig,
    update,
    frames=len(times),
    interval=450,
    repeat=True
)


# ------------------------------------------------------------
# 13. Save GIF
# ------------------------------------------------------------

OUT.parent.mkdir(exist_ok=True)

animation.save(
    OUT,
    writer=PillowWriter(fps=2),
    dpi=110
)

print("Saved:", OUT)

plt.close(fig)