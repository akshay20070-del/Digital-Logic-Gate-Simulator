"""
Sensor Simulator Module
=======================
Simulates 3-axis accelerometer readings (X, Y, Z) in m/s² for vehicle telemetry.

Note:
-----
This is strictly a SOFTWARE SIMULATION module for academic demonstration.
No physical accelerometer (such as MPU6050 or ADXL345) is interfaced.
All sensor outputs are mathematically modeled.
"""

import random
import math


class SensorSimulator:
    """
    Simulates tri-axial acceleration data of a moving vehicle.
    
    Standard Vehicle Coordinate System:
      - X-axis: Lateral acceleration (left / right steering maneuvers)
      - Y-axis: Longitudinal acceleration (forward acceleration / braking)
      - Z-axis: Vertical acceleration (gravity ~ 9.8 m/s² + road surface roughness)
    """

    def __init__(self):
        # Base physical parameters
        self.gravity = 9.80665  # Standard Earth gravity in m/s²
        
        # State tracking
        self.simulation_mode = "NORMAL"  # NORMAL, BUMP, BRAKING, ACCIDENT
        self.accident_frames_remaining = 0
        self.bump_frames_remaining = 0
        
        # Smooth random walk tracking
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = self.gravity

    def force_accident(self, duration_frames: int = 3):
        """
        Manually trigger an accident event.
        Queues violent shock readings (> 30-55 m/s²) for multiple consecutive frames.
        """
        self.accident_frames_remaining = duration_frames
        self.simulation_mode = "ACCIDENT"

    def force_bump(self):
        """
        Trigger a momentary speed bump or pothole (1 single frame spike).
        Demonstrates how the consecutive threshold filter rejects single-sample false alarms.
        """
        self.bump_frames_remaining = 1
        self.simulation_mode = "BUMP"

    def set_mode(self, mode: str):
        """Set simulation mode: 'NORMAL', 'BUMP', 'SHARP_TURN', 'ACCIDENT'."""
        self.simulation_mode = mode

    def get_reading(self) -> dict:
        """
        Generate and return the next instantaneous 3-axis acceleration sample.
        
        Returns:
            dict: {
                'x': float (m/s²),
                'y': float (m/s²),
                'z': float (m/s²),
                'state_description': str
            }
        """
        # 1. Accident State (Critical collision impact)
        if self.accident_frames_remaining > 0:
            self.accident_frames_remaining -= 1
            # Severe collision shock force: 30 - 60 m/s²
            x = round(random.choice([-1, 1]) * random.uniform(18.0, 35.0), 2)
            y = round(random.choice([-1, 1]) * random.uniform(25.0, 50.0), 2)
            z = round(random.choice([-1, 1]) * random.uniform(15.0, 30.0), 2)
            desc = "SIMULATED COLLISION IMPACT"
            
            if self.accident_frames_remaining == 0:
                self.simulation_mode = "NORMAL"
            return {'x': x, 'y': y, 'z': z, 'state_description': desc}

        # 2. Road Bump State (Impulse shock - single reading)
        if self.bump_frames_remaining > 0:
            self.bump_frames_remaining -= 1
            x = round(random.uniform(-1.0, 1.0), 2)
            y = round(random.uniform(-2.0, 2.0), 2)
            z = round(self.gravity + random.uniform(8.0, 12.0), 2)  # ~18 - 22 m/s²
            desc = "ROAD BUMP / POTHOLE (MOMENTARY SPIKE)"
            self.simulation_mode = "NORMAL"
            return {'x': x, 'y': y, 'z': z, 'state_description': desc}

        # 3. Normal Operating State (Cruising, subtle vibrations, gradual turns)
        if self.simulation_mode == "NORMAL":
            # Small road vibration and engine jitter
            x = round(random.gauss(0.0, 0.4), 2)
            y = round(random.gauss(0.0, 0.6), 2)
            z = round(self.gravity + random.gauss(0.0, 0.5), 2)
            desc = "NORMAL VEHICLE CRUISING"
            return {'x': x, 'y': y, 'z': z, 'state_description': desc}

        # Default fallback
        x = round(random.gauss(0.0, 0.3), 2)
        y = round(random.gauss(0.0, 0.4), 2)
        z = round(self.gravity + random.gauss(0.0, 0.3), 2)
        return {'x': x, 'y': y, 'z': z, 'state_description': "CRUISING"}

    def reset(self):
        """Reset sensor state back to standard stationary/normal cruising."""
        self.simulation_mode = "NORMAL"
        self.accident_frames_remaining = 0
        self.bump_frames_remaining = 0
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = self.gravity
