"""
GPS Simulator Module
====================
Generates simulated Global Positioning System (GPS) coordinates for vehicle tracking.

Note:
-----
This is strictly a SOFTWARE SIMULATION module for academic demonstration.
No physical GPS module (such as Neo-6M) or real satellite link is used.
Coordinates represent a demonstration route in a simulated metropolitan area.
"""

import random


class GPSSimulator:
    """
    Simulates vehicle geographical coordinates and telemetry.
    """

    def __init__(self, base_lat: float = 12.971598, base_lon: float = 77.594566):
        """
        Initialize GPS simulator with base geographic coordinates (Default: Tech Corridor).
        """
        self.base_lat = base_lat
        self.base_lon = base_lon
        
        # Current active coordinates
        self.latitude = base_lat
        self.longitude = base_lon
        
        # Vehicle dynamics simulation
        self.speed_kmh = 45.0
        self.heading_deg = 45.0
        self.is_frozen = False  # Freezes coordinates on crash impact

    def update_location(self) -> dict:
        """
        Advance vehicle location along simulated route if vehicle is moving.
        
        Returns:
            dict: {
                'latitude': float,
                'longitude': float,
                'speed_kmh': float,
                'maps_url': str,
                'tag': str
            }
        """
        if not self.is_frozen:
            # Small random drift simulating vehicle movement at road speed
            # ~0.00003 degrees is approx 3-4 meters per reading interval
            lat_delta = random.uniform(0.00001, 0.00003)
            lon_delta = random.uniform(0.00001, 0.00003)
            
            self.latitude += lat_delta
            self.longitude += lon_delta
            
            # Speed variation (40 - 65 km/h)
            self.speed_kmh = round(max(0.0, random.gauss(52.0, 3.0)), 1)
        else:
            self.speed_kmh = 0.0  # Vehicle halted after collision

        maps_url = self.get_google_maps_link()

        return {
            'latitude': round(self.latitude, 6),
            'longitude': round(self.longitude, 6),
            'speed_kmh': self.speed_kmh,
            'maps_url': maps_url,
            'tag': "[SIMULATED GPS DATA - ACADEMIC DEMONSTRATION]"
        }

    def freeze_location(self):
        """Freeze GPS coordinates (used when accident is detected)."""
        self.is_frozen = True
        self.speed_kmh = 0.0

    def unfreeze_location(self):
        """Resume simulated movement."""
        self.is_frozen = False
        self.speed_kmh = 45.0

    def get_google_maps_link(self) -> str:
        """Generate a Google Maps URL for the current simulated coordinates."""
        return f"https://www.google.com/maps?q={round(self.latitude, 6)},{round(self.longitude, 6)}"

    def reset(self):
        """Reset coordinates to base demonstration starting point."""
        self.latitude = self.base_lat
        self.longitude = self.base_lon
        self.speed_kmh = 45.0
        self.is_frozen = False
