# Hong Kong PM2.5 — Past 24 Hours

## Spatial Distribution

### [Open the interactive PM2.5 spatial map](https://yanyan-hub57.github.io/hong-kong-air-quality/site/map.html)

Explore PM2.5 measurements across 18 official Hong Kong air-quality monitoring stations over the past 24 hours.

The spatial map places PM2.5 measurements at the official geographic locations of 18 Hong Kong air-quality monitoring stations.

The spatial map places PM2.5 measurements at the official geographic locations of 18 Hong Kong air-quality monitoring stations.

Each vertical column represents one monitoring station. Column height and colour both encode measured PM2.5 concentration: lower values appear toward blue and purple, while higher values move through pink and red toward yellow. A fixed scale calculated from the full 24-hour dataset is used so that the same PM2.5 value has the same visual meaning at every hour.

The timeline allows the viewer to move through the past 24 hours, while Play/Pause reveals how the spatial pattern changes through time. Hovering identifies a monitoring station, and clicking a column reveals its exact PM2.5 measurement and time.

The station locations come from the Hong Kong Government's official Air Quality Monitoring Network geographic dataset. The map therefore adds geographic context that the abstract particle field intentionally does not show.

### Two views of the same phenomenon

The project uses two complementary experimental views of the same measurements:

**Particle Field — WHEN:** explores temporal change through an abstract data-driven form.

**Spatial Map — WHERE:** places the measurements back at their official monitoring locations to reveal spatial differences across Hong Kong.

The heatmap below acts as a more direct reference to the original station-by-time measurements.

## Particle Field

![Hong Kong PM2.5 Particle Field](out/particle-field.png)

### Interactive Particle Field

The particle field transforms 24 hours of PM2.5 measurements from 18 Hong Kong air-quality monitoring stations into a dynamic, interactive form.

Each particle band represents a monitoring station. PM2.5 concentration affects the deformation of the particle field and is also mapped to colour, moving from purple for lower values through pink and orange to yellow for higher values within this dataset.

As the timeline moves through the 24-hour period, the field changes according to the measurements recorded at each hour.

Click a particle to inspect its monitoring station, PM2.5 value, and time. Use the timeline or Play/Pause button to explore how the field changes over time.

[Open the interactive particle field →](https://yanyan-hub57.github.io/hong-kong-air-quality/site/)

The particle field is an abstract visual representation of measured data. It does not represent the geographic position of the monitoring stations or the physical shape and movement of individual PM2.5 particles.

## Data Overview

![Hong Kong PM2.5 — Past 24 Hours](out/plot.png)

The heatmap provides a more direct view of the original measurements. Each row represents a monitoring station, each column represents an hour, and each cell represents one PM2.5 measurement.

The heatmap acts as a reference for understanding the more experimental particle-field transformation.

### Animated Visualization

![Hong Kong PM2.5 animation](out/pm25-animation.gif)

The animation reveals the hourly measurements progressively, providing another way to observe change through time.

## The phenomenon

This project explores how PM2.5 air pollution changes across Hong Kong over a 24-hour period. PM2.5 is fine particulate matter in the air.

I wanted to compare measurements from different monitoring stations and ask: how does PM2.5 concentration vary across Hong Kong and across different hours of the day?

I chose this phenomenon because air pollution is normally invisible. Turning measured concentrations into visual form makes differences across time and monitoring stations easier to explore.

## The source

The data comes from the Hong Kong Environmental Protection Department's Air Quality Health Index (AQHI) service:

https://www.aqhi.gov.hk/en/download/past-24-hours-pollutant-concentration.html

The raw XML file is downloaded by `fetch.py` and stored as `data/hong-kong-air-quality-24h.xml`.

For the spatial visualization, official monitoring-station coordinates come from the Hong Kong Government Common Spatial Data Infrastructure (CSDI), using the Air Quality Monitoring Network dataset.

The geographic data is stored locally as `data/monitoring-stations.geojson`. All 18 PM2.5 monitoring stations used in the visualization were matched to official geographic coordinates.

The map data used by the browser visualization is generated locally as `site/pm25-map-data.json`, combining the committed PM2.5 measurements with the official station coordinates.

It contains hourly pollutant measurements from 18 air-quality monitoring stations. For this project, I use three fields: monitoring station, date and time, and PM2.5 concentration. PM2.5 is measured in µg/m³.

Most stations contain 24 valid PM2.5 measurements in this downloaded dataset, while some measurements are missing. Tuen Mun has no valid PM2.5 measurements in this particular 24-hour dataset.

Missing measurements are kept as missing rather than estimated or replaced with invented values.

## How the data becomes the visualization

The project uses the same measured dataset in several visual forms.

In the heatmap, time becomes horizontal position, monitoring station becomes vertical position, and PM2.5 concentration becomes colour intensity. Yellow represents lower concentrations, while orange and red represent higher concentrations. Grey represents missing measurements.

In the particle field, the same measurements are transformed into an abstract spatial system. Each monitoring station becomes a particle band. PM2.5 measurements influence the local deformation of the field, while colour provides an additional visual encoding of concentration.

The colour scale runs from purple for lower PM2.5 values through pink and orange to yellow for higher values within the current dataset.

Time becomes interaction: moving the timeline or pressing Play changes the field according to the measurements recorded at each hour.

This means the visualization follows the transformation:

**measured PM2.5 data → station and time structure → visual mapping → particle deformation → interaction**

## What the visualization shows and hides

The three representations reveal different aspects of the same dataset.

The heatmap makes the original station-by-time structure easy to compare and provides the most direct overview of the measurements.

The particle field intentionally sacrifices geographic and numerical readability to explore how measured environmental data can generate form, colour, movement, and interaction.

The spatial map restores geographic context by placing the measurements at the official locations of the 18 monitoring stations. Column height and colour reveal relative PM2.5 concentration, while the timeline reveals how this pattern changes over 24 hours.

The visualizations do not represent the continuous concentration of PM2.5 everywhere in Hong Kong. Measurements exist only at monitoring stations, so areas between stations should not be interpreted as measured pollution values.

The project also does not show other pollutants such as PM10, NO2, O3, or SO2. The particle geometry and glowing map columns are visual encodings of measured PM2.5 values rather than literal representations of physical pollution particles.

## Animation and interaction

I developed three complementary representations of the same dataset.

`plot.py` creates the static heatmap, which provides an overview of the original measurements.

`animate.py` creates an animated heatmap that reveals the measurements through time.

`interactive.py` creates the interactive particle field. The viewer can select particles to inspect individual measurements and use the timeline or Play/Pause control to move through the 24-hour period.

Together, these representations move from direct data comparison toward a more experimental and interactive interpretation while remaining connected to the original measurements.

## Run it

Fetch the source data:

```bash
uv run fetch.py
```

Create the static heatmap:

```bash
uv run plot.py
```

Create the animation:

```bash
uv run animate.py
```

Create the static particle field:

```bash
uv run particle_static.py
```

Create the interactive particle field:

```bash
uv run interactive.py
```

The interactive visualization is saved as `site/index.html`.

Open it locally in a web browser, or view the published version:

[Open the interactive particle field →](https://yanyan-hub57.github.io/hong-kong-air-quality/site/)

Prepare the official monitoring-station geography:

```bash
uv run fetch_stations.py