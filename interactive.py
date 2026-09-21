# /// script
# requires-python = ">=3.10"
# dependencies = ["plotly"]
# ///

from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

import plotly.graph_objects as go


# ------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------

HERE = Path(__file__).parent
DATA = HERE / "data" / "hong-kong-air-quality-24h.xml"

SITE = HERE / "site"
OUT = SITE / "index.html"


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

    if not pm25_text or pm25_text.strip() == "-":
        pm25 = None
    else:
        pm25 = float(pm25_text)

    records.append((station, time, pm25))


# ------------------------------------------------------------
# 4. Stations and times
# ------------------------------------------------------------

stations = sorted(set(record[0] for record in records))
times = sorted(set(record[1] for record in records))

print("Number of stations:", len(stations))
print("Number of times:", len(times))


# ------------------------------------------------------------
# 5. Build matrix
# ------------------------------------------------------------

lookup = {
    (station, time): pm25
    for station, time, pm25 in records
}

matrix = []

for station in stations:

    row = []

    for time in times:
        row.append(
            lookup.get((station, time))
        )

    matrix.append(row)


# ------------------------------------------------------------
# 6. Human-readable time labels
# ------------------------------------------------------------

# Full labels are used by the heatmap and hover interaction.
time_labels = [
    time.strftime("%d %b · %H:%M")
    for time in times
]

# Only show every third hour on the visible x-axis.
tick_values = time_labels[::3]

tick_text = [
    time.strftime("%d %b\n%H:%M")
    for time in times[::3]
]


# ------------------------------------------------------------
# 7. Custom hover information
# ------------------------------------------------------------

hover_text = []

for station_index, station in enumerate(stations):

    hover_row = []

    for time_index, time in enumerate(times):

        value = matrix[station_index][time_index]

        if value is None:
            value_text = "Missing measurement"
        else:
            value_text = f"{value:.1f} µg/m³"

        hover_row.append(
            f"<b>{station}</b><br>"
            f"{time.strftime('%d %b %Y · %H:%M')}<br>"
            f"PM2.5: {value_text}"
        )

    hover_text.append(hover_row)


# ------------------------------------------------------------
# 8. Interactive heatmap
# ------------------------------------------------------------

fig = go.Figure(

    data=go.Heatmap(

        z=matrix,

        x=time_labels,

        y=stations,

        text=hover_text,

        hovertemplate="%{text}<extra></extra>",

        colorscale=[
            [0.00, "#fff7bc"],
            [0.25, "#fee391"],
            [0.50, "#fec44f"],
            [0.75, "#fe9929"],
            [1.00, "#cc4c02"],
        ],

        colorbar=dict(
            title=dict(
                text="PM2.5<br>µg/m³"
            ),
            thickness=16,
            len=0.75
        ),

        xgap=1,
        ygap=1,

        hoverongaps=False
    )
)


# ------------------------------------------------------------
# 9. Layout
# ------------------------------------------------------------

fig.update_layout(

    title=dict(
        text=(
            "<b>HONG KONG PM2.5</b>"
            "<br>"
            "<span style='font-size:18px'>"
            "Past 24 Hours"
            "</span>"
            "<br>"
            "<span style='font-size:12px;color:#666'>"
            "18 monitoring stations · hourly measurements"
            "</span>"
        ),
        x=0.03,
        xanchor="left"
    ),

    font=dict(
        family="Arial, Helvetica, sans-serif",
        color="#202124"
    ),

    paper_bgcolor="#f7f7f5",
    plot_bgcolor="#f7f7f5",

    margin=dict(
        l=145,
        r=80,
        t=130,
        b=100
    ),

    height=720,

    xaxis=dict(
    title=dict(
        text="TIME",
        font=dict(size=11)
    ),

    side="bottom",

    tickmode="array",
    tickvals=tick_values,
    ticktext=tick_text,

    tickfont=dict(
        size=10,
        color="#555555"
    ),

    showgrid=False,
    zeroline=False,
    fixedrange=False
),
    yaxis=dict(
        title="",
        autorange="reversed",
        showgrid=False
    ),

    hoverlabel=dict(
        bgcolor="white",
        font_size=13,
        font_family="Arial"
    ),

    annotations=[
        dict(
            text=(
                "Hover over a cell to inspect a measurement"
                " · Blank cells indicate missing data"
            ),
            x=0,
            y=-0.14,
            xref="paper",
            yref="paper",
            showarrow=False,
            xanchor="left",
            font=dict(
                size=11,
                color="#666666"
            )
        ),
        dict(
            text=(
                "Source: Hong Kong Environmental "
                "Protection Department · AQHI"
            ),
            x=1,
            y=-0.14,
            xref="paper",
            yref="paper",
            showarrow=False,
            xanchor="right",
            font=dict(
                size=11,
                color="#666666"
            )
        )
    ]
)

# ------------------------------------------------------------
# 10. Station selector
# ------------------------------------------------------------

buttons = []

for station_index, station in enumerate(stations):

    buttons.append(
        dict(
            label=station,
            method="update",
            args=[
                {},
                {
                    "title": {
                        "text": (
                            "<b>HONG KONG PM2.5</b>"
                            "<br>"
                            "<span style='font-size:18px'>"
                            f"{station} · Past 24 Hours"
                            "</span>"
                            "<br>"
                            "<span style='font-size:12px;color:#666'>"
                            "Select another station or hover over the heatmap"
                            "</span>"
                        ),
                        "x": 0.03,
                        "xanchor": "left"
                    }
                }
            ]
        )
    )


fig.update_layout(

    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",

            x=1,
            xanchor="right",

            y=1.16,
            yanchor="top",

            showactive=True
        )
    ]
)

# ------------------------------------------------------------
# 11. Save interactive HTML
# ------------------------------------------------------------

SITE.mkdir(exist_ok=True)

fig.write_html(
    OUT,
    include_plotlyjs=True,
    full_html=True,
    config={
        "displayModeBar": True,
        "responsive": True,
        "displaylogo": False
    }
)

print("Saved:", OUT)