# Hong Kong PM2.5 — Past 24 Hours

## Particle Field

![Hong Kong PM2.5 Particle Field](out/particle-field.png)

This visualization transforms measured PM2.5 concentrations from 18 Hong Kong air-quality monitoring stations over 24 hours into an abstract particle field.

The particle surface is deformed by the measured PM2.5 values. Higher PM2.5 concentrations create stronger local displacement in the form.

The particle field is an abstract visual representation of the measurements. It does not represent the physical location or movement of individual PM2.5 particles.

## Data Overview

![Hong Kong PM2.5 — Past 24 Hours](out/plot.png)

The heatmap provides a more direct view of the original measurements across monitoring stations and time.

### Animated visualization

![Hong Kong PM2.5 animation](out/pm25-animation.gif)

### Interactive visualization

Explore the data interactively to inspect individual monitoring stations, times, and PM2.5 measurements.

[Open the interactive visualization →](https://yanyan-hub57.github.io/hong-kong-air-quality/site/)

## The phenomenon

This project explores how PM2.5 air pollution changes across Hong Kong over a 24-hour period. PM2.5 is fine particulate matter in the air. I wanted to compare measurements from different monitoring stations and ask: how does PM2.5 concentration vary across Hong Kong and across different hours of the day?

I chose this phenomenon because air pollution is normally invisible. Turning the measurements into a picture makes changes across time and monitoring locations easier to see and compare.

## The source

The data comes from the Hong Kong Environmental Protection Department's Air Quality Health Index (AQHI) service:

https://www.aqhi.gov.hk/en/download/past-24-hours-pollutant-concentration.html

The raw XML file is downloaded by `fetch.py` and stored as `data/hong-kong-air-quality-24h.xml`. It contains hourly pollutant measurements from 18 air-quality monitoring stations. For this visualization, I use the station name, date and time, and PM2.5 concentration. PM2.5 is measured in µg/m³.

Most stations contain 24 valid PM2.5 measurements in this dataset, while some stations have missing measurements. Tuen Mun has no valid PM2.5 measurements in the downloaded 24-hour period.

## What the picture shows

The picture transforms the PM2.5 measurements into a heatmap. Each row represents an air-quality monitoring station, each column represents an hour, and each cell represents one PM2.5 measurement.

Time becomes horizontal position, monitoring station becomes vertical position, and PM2.5 concentration becomes colour intensity. Lighter yellow cells represent lower PM2.5 concentrations, while orange and red cells represent higher concentrations. Grey cells represent missing data, not zero pollution.

This transformation makes temporal and station-to-station patterns visible in one picture. However, it hides the geographic locations of the monitoring stations and other pollutants such as PM10, NO2, O3, and SO2. It also does not estimate missing measurements; missing values remain visible as grey cells.

## Animation and interaction

I extended the static heatmap in two ways.

First, `animate.py` turns the 24-hour dataset into an animation. Each frame reveals another hour of measurements, so time is represented not only as horizontal position but also as movement.

Second, `interactive.py` creates an interactive HTML visualization. The heatmap allows the viewer to hover over individual cells to inspect the monitoring station, time, and exact PM2.5 measurement. Missing measurements remain blank instead of being estimated.

The static image gives an overview of the complete dataset, the animation reveals the measurements through time, and the interactive version allows the viewer to inspect individual values.

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

Create the interactive visualization:

```bash
uv run interactive.py
```

The interactive visualization is saved as `site/index.html`. Open this file in a web browser to explore individual PM2.5 measurements.

