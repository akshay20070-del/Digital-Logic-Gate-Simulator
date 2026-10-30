# Smart Accident Detection System - Software Module

## 1. Software Overview

The **Software Module** of the **Smart Accident Detection and Emergency Alert System** is an interactive desktop telemetry and digital signal processing simulator developed in Python. It models vehicle kinematics across three spatial axes, calculates dynamic acceleration vectors, filters out road surface noise (such as speed breakers and potholes), detects simulated vehicular collisions, and generates automated distress dispatches paired with simulated GPS coordinates.

> **ACADEMIC DISCLAIMER**: This application is strictly a **software-only simulation** designed for college mini-project demonstration in Electronics and Communication Engineering (ECE). It does not interface with physical hardware (e.g., MPU6050, Arduino, ESP32) nor send actual SMS or GSM network transmissions.

---

## 2. System Architecture & Components

```text
software/
├── main.py                 # Primary Tkinter Dashboard GUI & Execution Loop
├── accident_detection.py   # DSP Core: Vector Magnitude & Consecutive Filter
├── sensor_simulator.py     # Kinematics Simulator (X, Y, Z Axis Acceleration)
├── gps_simulator.py        # Simulated Satellite Coordinate & Navigation Generator
├── alert_manager.py        # Emergency Dispatch Composer & CSV Incident Logger
├── test_system.py          # Automated Test Suite for Validation & Viva Demo
├── requirements.txt        # Software Prerequisites & Standard Library Details
├── data/
│   ├── sample_sensor_data.csv   # Pre-recorded driving & collision telemetry
│   └── accident_history.csv     # Persistent storage for incident logs
└── screenshots/
    ├── README.md                # UI layout specification & color reference
    └── dashboard_preview.png    # Graphical preview of the software UI
```

---

## 3. Prerequisites & Installation

### Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu/Debian/Fedora), or macOS.
- **Python**: Version **3.8 or higher** (Tested on Python 3.10, 3.11, 3.12, 3.13, 3.14).
- **External Dependencies**: **None!** Built entirely using Python's standard libraries (`tkinter`, `math`, `csv`, `datetime`, `random`, `webbrowser`, `os`, `sys`).

### Python Installation Check
Verify that Python and Tkinter are available on your system:

```bash
# Check Python version
python --version

# Verify Tkinter module
python -c "import tkinter; print('Tkinter is ready! Version:', tkinter.TkVersion)"
```

*Note for Linux Users*: If Tkinter is not bundled by default on your Linux distribution, install it using:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

---

## 4. Execution Commands

### Running the Application
From the project workspace:

```bash
# Option 1: Navigate to the software folder and run main.py
cd software
python main.py

# Option 2: Run directly from the repository root
python software/main.py
```

### Running the Automated Test Suite
To verify all detection mathematics, filtering algorithms, and file operations before an academic viva or presentation:

```bash
cd software
python test_system.py
```

---

## 5. Technical Working Principles & Algorithms

### 5.1 Tri-Axial Acceleration Modeling (`sensor_simulator.py`)
In vehicle dynamics, an inertial measurement unit tracks motion along three mutually orthogonal axes:
- **X-Axis (Lateral)**: Steering maneuvers, centrifugal force during turns ($0 \pm 0.5\text{ m/s}^2$).
- **Y-Axis (Longitudinal)**: Acceleration and braking forces ($0 \pm 1.0\text{ m/s}^2$).
- **Z-Axis (Vertical)**: Standard gravitational field ($g \approx 9.81\text{ m/s}^2$) + road vibration.

During a simulated crash impact, large deceleration vectors are generated across all three axes ($|A| \ge 25\text{ to }60\text{ m/s}^2$).

### 5.2 Mathematical Formula & Accident Detection Algorithm (`accident_detection.py`)
The total scalar acceleration magnitude $A$ is calculated using the three-dimensional Euclidean norm:

$$A = \sqrt{X^2 + Y^2 + Z^2}$$

#### Digital Filtering Logic (Consecutive Sample Verification)
Single-sample impulse noise (such as driving over a sharp pothole or speed breaker) produces momentary acceleration spikes that could trigger false alarms. To prevent this, the detector implements a 2-stage verification algorithm:

```text
[Input Sample (X, Y, Z)]
           │
           ▼
[Compute Magnitude A = √(X² + Y² + Z²)]
           │
           ├─► Is A < 18.0 m/s²? ──────────────► [Status: NORMAL] (Reset Counter)
           │
           └─► Is A >= Threshold (25.0 m/s²)?
                     │
                     ├─► First Sample (Counter = 1) ─► [Status: WARNING] (Awaiting Confirmation)
                     │
                     └─► Second Sample (Counter >= 2) ─► [Status: ACCIDENT_DETECTED] 
                                                                │
                                                                ├─► Freeze GPS Position
                                                                ├─► Synthesize Emergency Alert
                                                                └─► Record in CSV History
```

### 5.3 Simulated GPS Geonavigation (`gps_simulator.py`)
- Emulates a vehicle traveling through a simulated coordinate grid (starting at Latitude `12.971598° N`, Longitude `77.594566° E`).
- Continuously increments coordinates with realistic vehicle velocity and road jitter.
- Generates an active, clickable Google Maps navigation URL:
  `https://www.google.com/maps?q={latitude},{longitude}`
- **Crash Freeze**: Upon confirmed collision, the GPS generator freezes the coordinates to represent the exact static accident location.

### 5.4 Emergency Alert Dispatcher (`alert_manager.py`)
When a crash is confirmed, the alert manager synthesizes a multi-line simulated distress dispatch:
- Incident timestamp
- Peak impact force in $\text{m/s}^2$ and $g$-force equivalent ($g = A / 9.80665$)
- Exact simulated geographic coordinates
- Google Maps web hyperlink
- Automatically writes the incident record to `data/accident_history.csv`

---

## 6. Graphical User Interface (GUI) Guide

| UI Section | Description |
| :--- | :--- |
| **Status Banner** | Prominent top banner with reactive color switching: Green (Normal), Yellow (Warning), Red (Accident). |
| **Telemetry Card** | Digital readouts of X, Y, Z acceleration axes, total magnitude, and dynamic graphic level meter. |
| **Threshold Control** | Interactive spinbox allowing real-time adjustment of collision threshold (Default: `25.0 m/s²`). |
| **Simulated GPS Card** | Displays current Latitude, Longitude, Speed, and buttons to open Google Maps or copy the link. |
| **Control Panel** | `Start Monitoring`, `Stop Monitoring`, `Simulate Accident`, and `Reset System` buttons. |
| **Emergency Dispatch Box** | Formatted live preview of the synthesized SOS broadcast notification. |
| **Incident History Log** | Scrollable table displaying recorded collision timestamps, peak forces, and coordinates. |

---

## 7. Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'tkinter'` | Python environment lacks Tkinter (common on minimal Linux). | On Ubuntu/Debian: `sudo apt-get install python3-tk`. On Windows, re-run Python installer and ensure "tcl/tk and IDLE" checkbox is ticked. |
| `PermissionError: [Errno 13] ... accident_history.csv` | CSV file is currently open in Microsoft Excel or another program. | Close Excel or other spreadsheet editors and re-run the application. |
| Browser does not open on clicking "Open in Google Maps" | Default browser association is missing in the OS. | Use the "Copy Coordinates Link" button and paste manually into any web browser. |
| Tkinter window appears too small or blurry on high-DPI screens | Windows display scaling. | Maximize the window; the layout utilizes responsive Tkinter grid/pack geometry. |
