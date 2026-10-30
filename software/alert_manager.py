"""
Alert Manager Module
====================
Handles generation of simulated emergency alert messages and persistent logging
of accident event history in CSV format.

Note:
-----
This is strictly a SOFTWARE SIMULATION module for college mini-project demonstration.
No real GSM/LTE module, SIM card, or paid SMS API (such as Twilio) is invoked.
All emergency alerts are synthesized and displayed locally.
"""

import os
import csv
from datetime import datetime


class AlertManager:
    """
    Synthesizes emergency dispatch alerts and manages persistent accident logs.
    """

    def __init__(self, history_file_path: str = None):
        """
        Initialize Alert Manager with target CSV storage path.
        """
        if history_file_path is None:
            # Default to data/accident_history.csv relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.history_file_path = os.path.join(data_dir, "accident_history.csv")
        else:
            self.history_file_path = history_file_path
            
        self._ensure_csv_headers()

    def _ensure_csv_headers(self):
        """Ensure the CSV history file exists with appropriate column headers."""
        if not os.path.exists(self.history_file_path):
            with open(self.history_file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp",
                    "Acceleration_Magnitude_mps2",
                    "Status",
                    "Latitude",
                    "Longitude",
                    "Google_Maps_URL"
                ])

    def generate_alert_message(self, magnitude: float, latitude: float, longitude: float, maps_url: str) -> str:
        """
        Synthesize formatted emergency alert text.
        
        Args:
            magnitude (float): Impact magnitude in m/s²
            latitude (float): Simulated latitude
            longitude (float): Simulated longitude
            maps_url (str): Google Maps navigation link
            
        Returns:
            str: Multi-line formatted simulated emergency dispatch notification.
        """
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        g_force = round(magnitude / 9.80665, 2)
        
        message = (
            "==========================================================\n"
            "🚨 [SIMULATED EMERGENCY ALERT] VEHICLE COLLISION DETECTED\n"
            "==========================================================\n"
            f"• Incident Timestamp : {timestamp_str}\n"
            f"• Impact Magnitude   : {magnitude:.2f} m/s² ({g_force:.2f} g)\n"
            f"• Severity Level     : CRITICAL IMPACT\n"
            "----------------------------------------------------------\n"
            "SIMULATED GPS LOCATION:\n"
            f"• Latitude           : {latitude:.6f}° N\n"
            f"• Longitude          : {longitude:.6f}° E\n"
            f"• Google Maps Link   : {maps_url}\n"
            "----------------------------------------------------------\n"
            "SIMULATED DISPATCH ACTIONS:\n"
            "✔ Automated Emergency Services Notification (Simulated)\n"
            "✔ Primary Family Contacts Alert Broadcast (Simulated)\n"
            "✔ GPS Telemetry Saved to Local Incident Log\n"
            "==========================================================\n"
            "[ACADEMIC NOTE]: This is a software simulation. No physical\n"
            "SMS or cellular network transmission was made.\n"
            "=========================================================="
        )
        return message

    def log_accident_event(self, magnitude: float, latitude: float, longitude: float, maps_url: str) -> dict:
        """
        Append detected accident record to persistent CSV file.
        
        Returns:
            dict: Record details of the logged event.
        """
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "Timestamp": timestamp_str,
            "Acceleration_Magnitude_mps2": f"{magnitude:.2f}",
            "Status": "ACCIDENT_CONFIRMED",
            "Latitude": f"{latitude:.6f}",
            "Longitude": f"{longitude:.6f}",
            "Google_Maps_URL": maps_url
        }

        try:
            with open(self.history_file_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    record["Timestamp"],
                    record["Acceleration_Magnitude_mps2"],
                    record["Status"],
                    record["Latitude"],
                    record["Longitude"],
                    record["Google_Maps_URL"]
                ])
        except Exception as e:
            print(f"[AlertManager Warning] Failed to write event to CSV: {e}")

        return record

    def load_history(self) -> list:
        """
        Read all historical accident events from CSV.
        
        Returns:
            list of dicts containing past accident records.
        """
        history = []
        if not os.path.exists(self.history_file_path):
            return history

        try:
            with open(self.history_file_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    history.append(row)
        except Exception as e:
            print(f"[AlertManager Warning] Failed to load history: {e}")

        return history

    def clear_history(self) -> bool:
        """
        Wipe the persistent CSV history file and reinitialize header.
        
        Returns:
            bool: True on success.
        """
        try:
            with open(self.history_file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp",
                    "Acceleration_Magnitude_mps2",
                    "Status",
                    "Latitude",
                    "Longitude",
                    "Google_Maps_URL"
                ])
            return True
        except Exception as e:
            print(f"[AlertManager Error] Failed to clear CSV: {e}")
            return False
