# Hong Kong PM2.5 — Past 24 Hours

![Hong Kong PM2.5 — Past 24 Hours](out/plot.png)

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

## Run it

```bash
uv run fetch.py
uv run plot.py

