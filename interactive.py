# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
import json


HERE = Path(__file__).parent
DATA = HERE / "data" / "hong-kong-air-quality-24h.xml"

SITE = HERE / "site"
OUT = SITE / "index.html"


# ------------------------------------------------------------
# 1. READ REAL PM2.5 DATA
# ------------------------------------------------------------

tree = ET.parse(DATA)
root = tree.getroot()

records = []

for item in root.iter("PollutantConcentration"):

    station = item.findtext("StationName")
    datetime_text = item.findtext("DateTime")
    pm25_text = item.findtext("PM2.5")

    if not station or not datetime_text:
        continue

    try:
        time = datetime.strptime(
            datetime_text,
            "%a, %d %b %Y %H:%M:%S %z"
        )
    except ValueError:
        continue

    if not pm25_text or pm25_text.strip() == "-":
        pm25 = None
    else:
        try:
            pm25 = float(pm25_text)
        except ValueError:
            pm25 = None

    records.append(
        (station, time, pm25)
    )


# ------------------------------------------------------------
# 2. STATIONS + TIMES
# ------------------------------------------------------------

stations = sorted({
    record[0]
    for record in records
})

times = sorted({
    record[1]
    for record in records
})

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


valid_values = [
    value
    for row in matrix
    for value in row
    if value is not None
]


minimum = min(valid_values)
maximum = max(valid_values)
average = sum(valid_values) / len(valid_values)


print("Stations:", len(stations))
print("Times:", len(times))
print("Minimum PM2.5:", round(minimum, 1))
print("Maximum PM2.5:", round(maximum, 1))
print("Average PM2.5:", round(average, 1))


# ------------------------------------------------------------
# 3. DATA FOR JAVASCRIPT
# ------------------------------------------------------------

data_for_web = {
    "stations": stations,

    "times": [
        time.strftime("%d %b · %H:%M")
        for time in times
    ],

    "matrix": matrix,

    "minimum": minimum,
    "maximum": maximum,
    "average": round(average, 1),
}

json_data = json.dumps(data_for_web)


# ------------------------------------------------------------
# 4. HTML
# ------------------------------------------------------------

html = r"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Hong Kong PM2.5 — Interactive Particle Field
</title>


<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;

    background: #000000;
    color: #ffffff;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    overflow-x: hidden;
}


body {
    min-height: 100vh;
}


.page {
    width: min(1400px, 94vw);
    margin: 0 auto;
    padding: 38px 0 40px;
}


/* ---------------- HEADER ---------------- */

header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 30px;
}


.eyebrow {
    color: #777777;
    font-size: 11px;
    letter-spacing: 0.16em;
    margin-bottom: 8px;
}


h1 {
    margin: 0;

    font-size: clamp(
        28px,
        4vw,
        54px
    );

    line-height: 0.95;
    letter-spacing: -0.04em;
}


.subtitle {
    margin-top: 12px;

    color: #8d8d8d;
    font-size: 13px;
}


.stats {
    display: flex;
    gap: 24px;

    text-align: right;
}


.stat-value {
    font-size: 20px;
    font-weight: bold;
}


.stat-label {
    margin-top: 4px;

    color: #666666;
    font-size: 9px;

    text-transform: uppercase;
    letter-spacing: 0.1em;
}


/* ---------------- PARTICLE AREA ---------------- */

.visual {
    position: relative;

    margin-top: 20px;

    width: 100%;
    height: min(58vw, 650px);

    min-height: 520px;

    overflow: hidden;
}


canvas {
    width: 100%;
    height: 100%;

    display: block;

    cursor: crosshair;
}


/* ---------------- INFORMATION PANEL ---------------- */

.info {
    position: absolute;

    right: 18px;
    bottom: 20px;

    width: 230px;

    padding: 16px 18px;

    background:
        rgba(12, 12, 12, 0.82);

    border:
        1px solid #252525;

    backdrop-filter:
        blur(12px);

    pointer-events: none;
}


.info-label {
    color: #666666;

    font-size: 9px;

    letter-spacing: 0.12em;
    text-transform: uppercase;
}


.info-value {
    margin-top: 5px;

    font-size: 16px;
    font-weight: bold;
}


.pm-value {
    margin-top: 12px;

    font-size: 32px;
    line-height: 1;
}


.unit {
    color: #777777;
    font-size: 11px;
}


/* ---------------- CONTROLS ---------------- */

.controls {
    border-top:
        1px solid #1d1d1d;

    padding-top: 20px;
}


.control-row {
    display: grid;

    grid-template-columns:
        80px 1fr 150px;

    align-items: center;

    gap: 20px;
}


button {
    height: 42px;

    background: #ffffff;
    color: #000000;

    border: 0;

    font-size: 11px;
    font-weight: bold;

    letter-spacing: 0.08em;

    cursor: pointer;
}


input[type="range"] {
    width: 100%;

    accent-color: #ff6a32;
}


.time-label {
    text-align: right;

    color: #aaaaaa;

    font-size: 12px;
}


/* ---------------- FOOTER ---------------- */

.footer {
    display: flex;
    justify-content: space-between;
    gap: 30px;

    margin-top: 20px;

    color: #555555;

    font-size: 10px;
    line-height: 1.6;
}


.instructions {
    color: #777777;
}


@media (max-width: 700px) {

    header {
        display: block;
    }

    .stats {
        margin-top: 24px;

        justify-content: space-between;

        text-align: left;
    }

    .visual {
        height: 580px;
    }

    .control-row {
        grid-template-columns:
            70px 1fr;
    }

    .time-label {
        grid-column: 1 / -1;
        text-align: left;
    }

    .footer {
        display: block;
    }

}

</style>

</head>


<body>

<div class="page">


<header>

<div>

<div class="eyebrow">
DATA → PARTICLES
</div>

<h1>
HONG KONG<br>
PM2.5
</h1>

<div class="subtitle">
Past 24 Hours · Interactive Particle Field
</div>

</div>


<div class="stats">

<div>
<div
    class="stat-value"
    id="minValue"
></div>

<div class="stat-label">
Minimum
</div>
</div>


<div>
<div
    class="stat-value"
    id="avgValue"
></div>

<div class="stat-label">
Average
</div>
</div>


<div>
<div
    class="stat-value"
    id="maxValue"
></div>

<div class="stat-label">
Maximum
</div>
</div>

</div>

</header>


<div class="visual">

<canvas id="particleCanvas"></canvas>


<div class="info">

<div class="info-label">
Selected measurement
</div>

<div
    class="info-value"
    id="stationName"
>
Click a particle to inspect
</div>

<div
    class="pm-value"
    id="pmValue"
>
—
</div>

<div class="unit">
µg/m³ PM2.5
</div>

<div
    class="info-value"
    id="measurementTime"
    style="
        margin-top:14px;
        font-size:11px;
        color:#888;
    "
>
—
</div>

</div>

</div>


<div class="controls">

<div class="control-row">

<button id="playButton">
PLAY
</button>

<input
    id="timeSlider"
    type="range"
    min="0"
    max="23"
    value="0"
    step="1"
>

<div
    class="time-label"
    id="currentTime"
></div>

</div>

</div>


<div class="footer">

<div class="instructions">
MOVE POINTER → DISTORT FIELD<br>
CLICK → SELECT MEASUREMENT<br>
PLAY → TRAVEL THROUGH 24 HOURS
</div>

<div>
Particle displacement is influenced by measured PM2.5 concentration.<br>
Source: Hong Kong Environmental Protection Department
</div>

</div>


</div>


<script>

const DATA = __DATA__;


/* ---------------------------------------------------------
   BASIC VALUES
--------------------------------------------------------- */

document.getElementById(
    "minValue"
).textContent =
    DATA.minimum.toFixed(1);


document.getElementById(
    "avgValue"
).textContent =
    DATA.average.toFixed(1);


document.getElementById(
    "maxValue"
).textContent =
    DATA.maximum.toFixed(1);


/* ---------------------------------------------------------
   CANVAS
--------------------------------------------------------- */

const canvas =
    document.getElementById(
        "particleCanvas"
    );

const ctx =
    canvas.getContext("2d");


let width = 0;
let height = 0;

let dpr =
    Math.min(
        window.devicePixelRatio || 1,
        2
    );


function resize() {

    const rect =
        canvas.getBoundingClientRect();

    width = rect.width;
    height = rect.height;

    canvas.width =
        width * dpr;

    canvas.height =
        height * dpr;

    ctx.setTransform(
        dpr,
        0,
        0,
        dpr,
        0,
        0
    );
}


window.addEventListener(
    "resize",
    resize
);

resize();


/* ---------------------------------------------------------
   PARTICLES
--------------------------------------------------------- */

const ROWS = 92;
const COLS = 126;

const particles = [];


for (
    let row = 0;
    row < ROWS;
    row++
) {

    for (
        let col = 0;
        col < COLS;
        col++
    ) {

        particles.push({

            u:
                col /
                (COLS - 1),

            v:
                row /
                (ROWS - 1),

            row,
            col

        });

    }

}


/* ---------------------------------------------------------
   STATE
--------------------------------------------------------- */

let currentFrame = 0;

let playing = false;

let timer = null;

let pointerX = -9999;
let pointerY = -9999;

let selectedParticle = null;


/* ---------------------------------------------------------
   DATA HELPERS
--------------------------------------------------------- */

function measurementAt(
    u,
    v,
    frame
) {

    const stationIndex =
        Math.min(
            DATA.stations.length - 1,

            Math.floor(
                v *
                DATA.stations.length
            )
        );


    const value =
        DATA.matrix[
            stationIndex
        ][
            frame
        ];


    return {
        stationIndex,
        value
    };

}


function normalize(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return 0;
    }


    return (
        value -
        DATA.minimum
    ) / Math.max(
        DATA.maximum -
        DATA.minimum,
        0.0001
    );

}


/* ---------------------------------------------------------
   COLOUR
--------------------------------------------------------- */

function particleColor(t, alpha) {

    t = Math.max(
        0,
        Math.min(1, t)
    );

    let r;
    let g;
    let b;

    // Low PM2.5: purple
    // Medium PM2.5: magenta / orange
    // High PM2.5: yellow

    if (t < 0.33) {

        const p = t / 0.33;

        r = 78 + p * 92;
        g = 32 + p * 18;
        b = 145 + p * 5;

    } else if (t < 0.66) {

        const p =
            (t - 0.33) / 0.33;

        r = 170 + p * 85;
        g = 50 + p * 55;
        b = 150 - p * 95;

    } else {

        const p =
            (t - 0.66) / 0.34;

        r = 255;
        g = 105 + p * 105;
        b = 55 - p * 15;

    }

    return (
        "rgba(" +
        Math.round(r) + "," +
        Math.round(g) + "," +
        Math.round(b) + "," +
        alpha +
        ")"
    );
}


/* ---------------------------------------------------------
   PARTICLE POSITION
--------------------------------------------------------- */

function positionParticle(
    particle,
    time
) {

    const u =
        particle.u;

    const v =
        particle.v;


    const measurement =
        measurementAt(
            u,
            v,
            currentFrame
        );


    const dataStrength =
        normalize(
            measurement.value
        );


    /*
       Organic particle form.
       PM2.5 modifies the local displacement.
    */

    const angle =
        u *
        Math.PI *
        2;


    const vertical =
        (v - 0.5) *
        2;


    let radius =
        0.31 +
        0.055 *
        Math.sin(
            angle * 3 +
            vertical * 3
        );


    radius +=
        0.055 *
        Math.cos(
            angle * 5 -
            vertical * 4
        );


    radius +=
        dataStrength *
        0.12;


    radius +=
        Math.sin(
            time * 0.00055 +
            angle * 2 +
            vertical * 5
        ) *
        0.018;


    let x =
        Math.cos(angle) *
        radius;


    let z =
        Math.sin(angle) *
        radius;


    let y =
        vertical *
        0.34;


    x +=
        Math.sin(
            vertical * 5 +
            time * 0.00035
        ) *
        0.045;


    z +=
        Math.cos(
            vertical * 4 -
            time * 0.00025
        ) *
        0.035;


    y +=
        Math.sin(
            angle * 3 +
            time * 0.00025
        ) *
        0.055 *
        (
            0.4 +
            dataStrength
        );


    /*
       Rotate the object.
    */

    const rotation =
        -0.65 +
        Math.sin(
            time * 0.00008
        ) *
        0.08;


    const rx =
        x *
        Math.cos(rotation) -
        z *
        Math.sin(rotation);


    const rz =
        x *
        Math.sin(rotation) +
        z *
        Math.cos(rotation);


    /*
       Perspective.
    */

    const perspective =
        1 /
        (
            1.35 -
            rz * 0.45
        );


    let screenX =
        width * 0.50 +
        rx *
        width *
        0.58 *
        perspective;


    let screenY =
        height * 0.50 +
        y *
        height *
        0.82 *
        perspective;


    /*
       Pointer distortion.
    */

    const dx =
        screenX -
        pointerX;

    const dy =
        screenY -
        pointerY;

    const distance =
        Math.sqrt(
            dx * dx +
            dy * dy
        );


    if (
        distance < 120 &&
        distance > 0
    ) {

        const force =
            (
                1 -
                distance / 120
            ) *
            22;


        screenX +=
            dx /
            distance *
            force;


        screenY +=
            dy /
            distance *
            force;

    }


    return {

        x: screenX,
        y: screenY,

        depth: rz,

        dataStrength,

        stationIndex:
            measurement.stationIndex,

        value:
            measurement.value

    };

}


/* ---------------------------------------------------------
   DRAW
--------------------------------------------------------- */

function draw(time) {

    ctx.clearRect(
        0,
        0,
        width,
        height
    );


    const projected = [];


    for (
        const particle
        of particles
    ) {

        const position =
            positionParticle(
                particle,
                time
            );


        projected.push({
            particle,
            ...position
        });

    }


    projected.sort(
        (a, b) =>
            a.depth -
            b.depth
    );


    for (
        const p
        of projected
    ) {

        const depthLight =
            Math.max(
                0.25,
                Math.min(
                    1,
                    0.65 +
                    p.depth
                )
            );


        const isSelected =
    selectedParticle &&
    p.stationIndex ===
        selectedParticle.stationIndex;


const radius =
    isSelected
        ? 2.8
        : 1.0 +
          p.dataStrength *
          1.35;


const particleAlpha =
    selectedParticle
        ? (
            isSelected
                ? 1.0
                : depthLight * 0.22
          )
        : depthLight;


        ctx.beginPath();

        ctx.arc(
            p.x,
            p.y,
            radius,
            0,
            Math.PI * 2
        );


        ctx.fillStyle =
    particleColor(
        p.dataStrength,
        particleAlpha
    );


        ctx.fill();

    }


    requestAnimationFrame(draw);

}


requestAnimationFrame(draw);


/* ---------------------------------------------------------
   POINTER
--------------------------------------------------------- */

canvas.addEventListener(
    "pointermove",
    function(event) {

        const rect =
            canvas.getBoundingClientRect();

        pointerX =
            event.clientX -
            rect.left;

        pointerY =
            event.clientY -
            rect.top;

    }
);


canvas.addEventListener(
    "pointerleave",
    function() {

        pointerX = -9999;
        pointerY = -9999;

    }
);


/* ---------------------------------------------------------
   CLICK → SELECT DATA
--------------------------------------------------------- */

canvas.addEventListener(
    "click",
    function(event) {

        const rect =
            canvas.getBoundingClientRect();

        const clickX =
            event.clientX -
            rect.left;

        const clickY =
            event.clientY -
            rect.top;


        let closest = null;
        let closestDistance = 40;


        const now =
            performance.now();


        for (
            const particle
            of particles
        ) {

            const p =
                positionParticle(
                    particle,
                    now
                );


            const dx =
                p.x -
                clickX;

            const dy =
                p.y -
                clickY;

            const distance =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );


            if (
                distance <
                closestDistance
            ) {

                closestDistance =
                    distance;

                closest = p;

            }

        }


        if (!closest) {
            return;
        }


        selectedParticle =
            closest;


        const station =
            DATA.stations[
                closest.stationIndex
            ];


        document.getElementById(
            "stationName"
        ).textContent =
            station;


        document.getElementById(
            "pmValue"
        ).textContent =
            closest.value === null
            ? "Missing"
            : closest.value.toFixed(1);


        document.getElementById(
            "measurementTime"
        ).textContent =
            DATA.times[
                currentFrame
            ];

    }
);


/* ---------------------------------------------------------
   TIME
--------------------------------------------------------- */

const slider =
    document.getElementById(
        "timeSlider"
    );


slider.max =
    DATA.times.length - 1;


function updateFrame(
    frame
) {

    currentFrame =
        Number(frame);


    slider.value =
        currentFrame;


    document.getElementById(
        "currentTime"
    ).textContent =
        DATA.times[
            currentFrame
        ];


    if (selectedParticle) {

        const stationIndex =
            selectedParticle
                .stationIndex;


        const value =
            DATA.matrix[
                stationIndex
            ][
                currentFrame
            ];


        document.getElementById(
            "pmValue"
        ).textContent =
            value === null
            ? "Missing"
            : value.toFixed(1);


        document.getElementById(
            "measurementTime"
        ).textContent =
            DATA.times[
                currentFrame
            ];

    }

}


slider.addEventListener(
    "input",
    function() {

        updateFrame(
            slider.value
        );

    }
);


updateFrame(0);


/* ---------------------------------------------------------
   PLAY / PAUSE
--------------------------------------------------------- */

const playButton =
    document.getElementById(
        "playButton"
    );


playButton.addEventListener(
    "click",
    function() {

        playing =
            !playing;


        playButton.textContent =
            playing
            ? "PAUSE"
            : "PLAY";


        if (playing) {

            clearInterval(timer);


            timer =
                setInterval(
                    function() {

                        let next =
                            currentFrame + 1;


                        if (
                            next >=
                            DATA.times.length
                        ) {
                            next = 0;
                        }


                        updateFrame(
                            next
                        );

                    },
                    700
                );

        } else {

            clearInterval(timer);

        }

    }
);

</script>
<div class="pm-legend">
    <div class="legend-title">PM2.5 CONCENTRATION</div>

    <div class="legend-scale"></div>

    <div class="legend-labels">
        <span>LOW · 4.4</span>
        <span>HIGH · 32.7</span>
    </div>

    <div class="legend-unit">µg/m³</div>
</div>

<style>
.pm-legend {
    position: fixed;
    left: 32px;
    bottom: 105px;
    width: 250px;

    color: white;
    font-family: Arial, Helvetica, sans-serif;

    z-index: 20;
    pointer-events: none;
}

.legend-title {
    margin-bottom: 10px;

    font-size: 10px;
    letter-spacing: 1.5px;

    color: #777;
}

.legend-scale {
    width: 100%;
    height: 5px;

    border-radius: 10px;

    background: linear-gradient(
        90deg,
        rgb(78, 32, 145) 0%,
        rgb(170, 50, 150) 33%,
        rgb(255, 105, 55) 66%,
        rgb(255, 210, 40) 100%
    );
}

.legend-labels {
    display: flex;
    justify-content: space-between;

    margin-top: 8px;

    font-size: 10px;
    letter-spacing: 0.5px;

    color: #aaa;
}

.legend-unit {
    margin-top: 4px;

    font-size: 9px;

    color: #555;
}
</style>
</body>

</html>
"""


html = html.replace(
    "__DATA__",
    json_data
)


# ------------------------------------------------------------
# 5. SAVE
# ------------------------------------------------------------

SITE.mkdir(
    parents=True,
    exist_ok=True
)

OUT.write_text(
    html,
    encoding="utf-8"
)

print("Saved:", OUT)