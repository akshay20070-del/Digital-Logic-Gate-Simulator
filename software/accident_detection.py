"""
Accident Detection Engine Module
=================================
Implements digital signal processing logic to detect vehicle accidents
from 3-axis acceleration telemetry.

Mathematical Formula:
---------------------
Total Acceleration Magnitude (A):
    A = sqrt(X^2 + Y^2 + Z^2)

Detection Principle:
--------------------
1. Calculate the instantaneous magnitude A.
2. Compare A with a preset Acceleration Threshold (e.g., 25.0 m/s²).
3. If A exceeds the threshold for N consecutive samples (default N = 2),
   a confirmed collision is declared.
4. Single-sample spikes (e.g., speed bumps or potholes) only trigger
   a transient warning, successfully eliminating false positive alerts.
"""

import math


class AccidentDetector:
    """
    Evaluates acceleration vectors and detects vehicle collision events.
    """

    def __init__(self, threshold_accel: float = 25.0, consecutive_required: int = 2):
        """
        Initialize detector with detection parameters.
        
        Args:
            threshold_accel (float): Acceleration threshold in m/s² (default: 25.0)
            consecutive_required (int): Required consecutive high readings to confirm crash (default: 2)
        """
        self.threshold_accel = threshold_accel
        self.consecutive_required = consecutive_required
        
        # Internal counters and states
        self.consecutive_count = 0
        self.accident_triggered = False
        self.last_magnitude = 9.81
        self.status = "NORMAL"  # "NORMAL", "WARNING", "ACCIDENT_DETECTED"

    @staticmethod
    def calculate_magnitude(x: float, y: float, z: float) -> float:
        """
        Calculate scalar acceleration magnitude using Euclidean norm:
        A = sqrt(X^2 + Y^2 + Z^2)
        
        Args:
            x (float): Lateral acceleration in m/s²
            y (float): Longitudinal acceleration in m/s²
            z (float): Vertical acceleration in m/s²
            
        Returns:
            float: Acceleration magnitude rounded to 2 decimal places.
        """
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        return round(magnitude, 2)

    def process_reading(self, x: float, y: float, z: float) -> dict:
        """
        Process a new telemetry reading and determine accident status.
        
        Args:
            x (float): X-axis acceleration
            y (float): Y-axis acceleration
            z (float): Z-axis acceleration
            
        Returns:
            dict: {
                'magnitude': float,
                'status': str ('NORMAL', 'WARNING', 'ACCIDENT_DETECTED'),
                'is_new_accident': bool,
                'consecutive_count': int,
                'threshold': float
            }
        """
        magnitude = self.calculate_magnitude(x, y, z)
        self.last_magnitude = magnitude
        is_new_accident = False

        if magnitude >= self.threshold_accel:
            self.consecutive_count += 1
            
            if self.consecutive_count >= self.consecutive_required:
                self.status = "ACCIDENT_DETECTED"
                if not self.accident_triggered:
                    is_new_accident = True
                    self.accident_triggered = True
            else:
                self.status = "WARNING"
        elif magnitude >= 18.0:
            # Elevated vibration / hard maneuver but below crash threshold
            self.consecutive_count = 0
            if not self.accident_triggered:
                self.status = "WARNING"
        else:
            self.consecutive_count = 0
            if not self.accident_triggered:
                self.status = "NORMAL"

        return {
            'magnitude': magnitude,
            'status': self.status,
            'is_new_accident': is_new_accident,
            'consecutive_count': self.consecutive_count,
            'threshold': self.threshold_accel
        }

    def set_threshold(self, new_threshold: float):
        """Update detection threshold in m/s²."""
        self.threshold_accel = max(10.0, float(new_threshold))

    def set_consecutive_required(self, count: int):
        """Update consecutive count required for verification."""
        self.consecutive_required = max(1, int(count))

    def reset(self):
        """Reset internal detector state."""
        self.consecutive_count = 0
        self.accident_triggered = False
        self.status = "NORMAL"
        self.last_magnitude = 9.81
