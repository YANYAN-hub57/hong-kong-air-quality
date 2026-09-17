# Process

## Tools

I used VS Code to edit and run the project, GitHub to store the repository and track my commits, and `uv` to run the Python scripts.

I used Python to fetch, inspect, and transform the data. The raw data comes from the Hong Kong Environmental Protection Department's AQHI service. I used `xml.etree.ElementTree` to read the XML file and Matplotlib to create the final visualization.

I also used ChatGPT to help me understand the XML structure, debug Python errors, and develop the visualization. I checked the suggested code by running it locally and inspecting the actual data before using it in the final project.

## Kept

I kept the idea of using a heatmap for the final visualization. My first visualization focused on the PM2.5 measurements from Central/Western as a line chart, but this only showed one monitoring station.

After checking the dataset, I found 18 monitoring stations and up to 24 hourly measurements for each station. I changed the visualization to a heatmap because it makes both changes over time and differences between stations visible in one picture.

I also kept missing measurements as visible grey cells instead of replacing them with invented values. This makes the missing data clear to the viewer.

## Rejected

I rejected the first line-chart version because it only represented Central/Western and hid most of the available dataset.

During development, I also created a file called `inspect.py` to inspect the XML data. This caused an import error because `inspect` is also the name of a Python standard-library module used by Matplotlib. I renamed the file to `check_data.py`, which fixed the conflict.

I did not silently remove or estimate missing PM2.5 measurements. Some stations have fewer than 24 valid values, and Tuen Mun has no valid PM2.5 measurements in this downloaded dataset. I kept these gaps visible rather than creating values that were not present in the source data.