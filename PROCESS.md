# Process

## Tools

I used VS Code to edit and run the project, GitHub to store the repository and track my commits, and `uv` to run the Python scripts.

I used Python to fetch, inspect, and transform the data. The raw data comes from the Hong Kong Environmental Protection Department's AQHI service. I used `xml.etree.ElementTree` to read the XML file and Matplotlib to create the static heatmap, animation, and static particle-field experiments.

For the final interactive particle field, Python processes the original measurements and generates an HTML visualization. The browser-based visualization uses JavaScript and Canvas to render and animate the particles and provide interaction.

I also used ChatGPT to help me understand the XML structure, debug Python errors, explore visualization approaches, and develop the interactive particle-field code. I checked the suggested code by running it locally, inspecting the actual data, and comparing the visual output with the source measurements before keeping it in the project.

## Early exploration

My first visualization focused on PM2.5 measurements from Central/Western as a line chart. This helped me confirm that I could correctly parse timestamps and convert PM2.5 values from the XML file into numbers.

However, the line chart represented only one monitoring station and therefore hid most of the available dataset.

After inspecting the complete dataset, I found 18 monitoring stations and up to 24 hourly measurements for each station. I changed the visualization to a heatmap so that changes across both monitoring stations and time could be visible in one picture.

## Kept

I kept the heatmap as a direct reference visualization. Each row represents a monitoring station, each column represents an hour, and colour represents PM2.5 concentration.

I also kept missing measurements visible instead of replacing them with estimated values. This was important because I wanted the visualization to remain connected to the measurements actually contained in the downloaded dataset.

Later, even after developing the particle field, I kept the heatmap because it provides a useful reference for understanding the more abstract visualization.

## Rejected and debugging

I rejected the first single-station line chart as the final visualization because it represented only Central/Western and hid most of the dataset.

During development, I created a file called `inspect.py` to inspect the XML data. This caused an import error because `inspect` is also the name of a Python standard-library module used by Matplotlib. I renamed the file to `check_data.py`, which fixed the conflict.

I also rejected the idea of interpolating missing PM2.5 measurements. Some stations have fewer than 24 valid measurements, and Tuen Mun has no valid PM2.5 measurements in this downloaded dataset. I kept these values missing rather than creating measurements that were not present in the source.

## Animation iteration

After creating the static heatmap, I explored how time could become part of the visualization rather than only an x-axis position.

I created `animate.py` to reveal the PM2.5 measurements hour by hour. I kept the same colour scale throughout the animation so that colour retains a consistent meaning between frames.

This experiment helped lead to the idea that the final visualization could change continuously as the viewer moves through the 24-hour dataset.

## Particle field iteration

I then experimented with a more abstract way of representing the same PM2.5 measurements.

I first created `particle_static.py`, which transforms the station-by-time data into a static particle field. Instead of displaying measurements only as rectangular heatmap cells, I used the values to influence a continuous field made from particles.

Each particle band represents a monitoring station. PM2.5 concentration influences the deformation of the field and is also mapped to colour. Within this dataset, lower concentrations move toward purple, while higher concentrations move through pink and orange toward yellow.

The particle geometry is not intended to represent the physical shape of PM2.5 pollution. It is a data-driven abstraction generated from the measured values.

## Interactive particle field

I developed the static experiment into the final interactive visualization using `interactive.py`.

The Python script reads and processes the same XML dataset and generates `site/index.html`. In the browser, JavaScript and Canvas render the particle field and provide the interaction.

The visualization includes a 24-hour timeline and Play/Pause control. Moving through time changes the field according to the PM2.5 measurements recorded at each hour.

The viewer can also select a particle to inspect its monitoring station, exact PM2.5 measurement, and time. This was important because the particle field is visually abstract, so the interaction provides a way to return to the underlying measured value.

Colour also acts as a second data encoding. Lower PM2.5 concentrations are shown toward purple, while higher concentrations move toward yellow.

## Final decision

I kept both the heatmap and particle field because they serve different purposes.

The heatmap provides a direct overview of the original station-by-time structure and makes comparisons relatively easy.

The particle field is more experimental. It sacrifices some immediate numerical readability in order to explore how environmental measurements can generate form, colour, movement, and interaction.

The interactive information panel reconnects this abstract form to the original data by allowing individual measurements to be inspected.

Across all versions, missing measurements remain missing. I did not interpolate or invent PM2.5 values that were not present in the original dataset.