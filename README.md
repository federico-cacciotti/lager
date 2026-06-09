# LAGER

Live Attitude and Gimbal Error Resolver: a Python-based controller for UAV payload systems, designed to manage and coordinate a drone (DJI M600) and a gimbal (Gremsy T7) for autonomous Point-of-Interest (POI) tracking. The system reads a YAML configuration file, establishes serial connections to the hardware, logs telemetry data, and continuously points the gimbal at a fixed geographic target while the UAV moves.

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Hardware](#hardware)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Modules](#modules)
- [Tests](#tests)
- [TODO](#todo)

---

## Overview

The controller runs on a companion computer onboard the UAV (tested on Raspberry Pi). At startup it:

1. Loads a YAML configuration file.
2. Instantiates and connects to the drone (DJI M600 via DJI OSDK over serial) and the gimbal (Gremsy T7 via MAVLink over serial).
3. Starts telemetry logging for both devices to timestamped CSV files.
4. Optionally starts a live terminal display (powered by `rich`) showing real-time telemetry panels and the last log lines.
5. Continuously reads the UAV GPS position and computes the azimuth/elevation from the UAV to the POI using `pymap3d`, then commands the gimbal pitch accordingly.

---

## Repository Structure

```
lager/
├── cli.py                  # Rich-based live terminal display
├── Controller.py           # Main orchestration class
├── DataLoader.py           # Generic data loading utilities
├── decode_telemetry.py     # Offline telemetry decoding and plotting
├── follow_POI.py           # End-to-end POI tracking entry point
├── parameters.py           # Global parameters and paths
├── POI.py                  # POI class and gimbal tracking logic
├── requirements.txt        # Python dependencies
├── config/
│   ├── follow_POI_config.yaml          # Config for POI tracking flight
│   ├── move_gimbal_config.yaml         # Config for gimbal movement tests
│   ├── show_telemetry_config.yaml      # Config for live telemetry display
│   └── show_telemetry_sim_config.yaml  # Config for simulated telemetry display
├── data/
│   └── current             # Symlink to the most recent telemetry run folder
├── Drones/
│   └── DJI_M600/           # DJI M600 driver (connection, telemetry, utils)
├── Gimbals/
│   └── Gremsy_T7/          # Gremsy T7 driver (MAVLink, telemetry, goto)
└── tests/
    ├── data/
    │   └── gimbal_motion/   # Logged data from gimbal movement tests
    ├── move_gimbal.py       # Gimbal movement test
    ├── plot_telemetry.py    # Telemetry plotting utilities
    ├── show_telemetry.py    # Live telemetry display test
    └── show_telemetry_sim.py# Simulated telemetry display test
```

---

## Hardware

| Component | Model | Interface |
|-----------|-------|-----------|
| Drone | DJI M600 | Serial (DJI OSDK), `/dev/serial0` |
| Gimbal | Gremsy T7 | Serial (MAVLink), `/dev/ttyAMA4` |
| Companion computer | Raspberry Pi (or equivalent) | — |
| Status LED | — | GPIO pin 17 (BCM) |

---

## Requirements

Python 3.8 or later is recommended. Install dependencies with:

```bash
pip install -r requirements.txt
```

Key dependencies:

| Package | Purpose |
|---------|---------|
| `pymavlink` | MAVLink communication with Gremsy T7 |
| `pyserial` | Serial communication |
| `pymap3d` | Geodetic ↔ AER coordinate conversion for POI pointing |
| `rich` | Live terminal display |
| `pandas` / `numpy` | Telemetry data handling |
| `matplotlib` | Telemetry plotting |
| `pyyaml` | Configuration file parsing |

---

## Installation

```bash
git clone https://github.com/POLOCALC/lager.git
cd lager
pip install -r requirements.txt
```

---

## Configuration

All behaviour is controlled through a YAML configuration file. A complete example for POI tracking:

```yaml
Controller:
  name: Lab Test Controller
  display:
    enable: True
    refresh_rate: 2  # Hz

Drone:
  name: DJI M600
  simulator: False
  connection:
    type: serial
    protocol: DJI OSDK
    port: /dev/serial0
    baudrate: 115200
    timeout: 3
  telemetry:
    frequency: 50  # Hz

Gimbal:
  name: Gremsy T7
  simulator: False
  connection:
    type: serial
    protocol: mavlink
    port: /dev/ttyAMA4
    baudrate: 115200
    timeout: 3
  telemetry:
    heartbeat_frequency: 1  # Hz
    frequency: 50  # Hz

POI:
  name: Target
  latitude: 37.7749
  longitude: -122.4194
  altitude: 30.0       # meters above sea level
  max_distance: 700.0  # meters; tracking is paused if UAV is farther than this
```

Set `simulator: True` for either device to run without physical hardware (synthetic telemetry data will be generated).

---

## Usage

Run the main scripts from the project root:

```bash
# POI tracking (requires drone + gimbal connected)
python3 follow_POI.py

# Decode and inspect previously logged telemetry files
python3 decode_telemetry.py
```

Run test scripts from the `tests/` directory:

```bash
cd tests/

# Live telemetry display only
python3 show_telemetry.py

# Simulated telemetry display (no hardware needed)
python3 show_telemetry_sim.py

# Move gimbal to specific angles
python3 move_gimbal.py

# Plot logged telemetry data
python3 plot_telemetry.py
```

Press **Ctrl+C** to stop any running script gracefully; telemetry logging will be stopped and devices disconnected cleanly.

Each run creates a timestamped folder under `data/` containing the log file and a copy of the configuration used. A `data/current` symlink is automatically updated to point to the latest run folder.

---

## Modules

### `Controller`
The central orchestrator. Loaded with a YAML config file, it:
- Instantiates the drone and gimbal objects via `get_drone()` / `get_gimbal()`.
- Instantiates the `POI` object via `get_POI()`.
- Exposes `connect()`, `disconnect()`, `start_telemetry()`, `stop_telemetry()`.
- Optionally starts the `cli.live_display()` thread.

### `POI`
Represents a fixed geographic point of interest. Key methods:
- `start_tracking(uav, gimbal)` — starts a background thread that polls the UAV position at 10 Hz, computes the gimbal pitch via `pymap3d.geodetic2aer`, and sends a `gimbal.goto()` command.
- `stop_tracking()` — stops the tracking thread.
- `distance(uav_lat, uav_lon, uav_alt)` — returns the 3-D Euclidean distance (metres) between the UAV and the POI via ECEF coordinates.

Pitch computation:
```python
az, el, rng = pymap3d.geodetic2aer(poi_lat, poi_lon, poi_alt,
                                    uav_lat, uav_lon, uav_alt, deg=True)
gimbal_pitch = -el   # negative because elevation down = positive pitch-down command
```

### `Drones/DJI_M600`
Driver for the DJI M600 using the DJI OSDK protocol over serial. Provides:
- Serial connection management.
- Telemetry subscription and background logging.
- A `rich` panel renderer for the live display.

### `Gimbals/Gremsy_T7`
Driver for the Gremsy T7 using MAVLink over serial. Provides:
- Heartbeat loop and MAVLink session management.
- `goto(yaw, pitch, roll, wait)` for absolute angle commanding.
- Telemetry subscription and background logging.
- A `rich` panel renderer for the live display.

### `cli`
Builds and refreshes a `rich` `Live` layout with three panes:
- **Drone panel** — real-time drone telemetry.
- **Gimbal panel** — real-time gimbal telemetry.
- **Footer** — last N lines of the log file, colour-coded by log level.

### `GPIO`
Controls a status LED on a Raspberry Pi GPIO pin (BCM pin 17 by default). The LED reflects the controller lifecycle:

| LED state | Meaning |
|-----------|----------|
| Off | Controller not running / disconnected |
| Solid on | Initialising or connected, telemetry idle |
| Blinking | Telemetry acquisition in progress |

The `LED` class wraps `RPi.GPIO` and handles the blink loop in a daemon thread. If `RPi.GPIO` is not available (e.g. on a development machine) it fails silently and the rest of the code is unaffected. The LED pin and enable flag are configured via `parameters.py` (`LED_INDICATOR_PIN`, `ENABLE_LED_INDICATOR`).

---

## Tests

| Script | Location | Description |
|--------|----------|-------------|
| `follow_POI.py` | root | Full end-to-end POI tracking run |
| `decode_telemetry.py` | root | Load and print a saved telemetry binary file |
| `show_telemetry.py` | `tests/` | Live display with real hardware |
| `show_telemetry_sim.py` | `tests/` | Live display with simulated data |
| `move_gimbal.py` | `tests/` | Command the gimbal to a sequence of angles |
| `plot_telemetry.py` | `tests/` | Plot logged telemetry data with matplotlib |

---

## TODO
- POI pointing track (HIGH PRIORITY)
    - add a dynamic correction related to the uav attitude (yaw, pitch, roll)

- DJI M600
    - understand heading: from magnetometer? from rtk?
    - simulate data writing on file
    - separate graphic function from main file

- Gremsy T7
    - add graphic features
    - separate graphic function from main file