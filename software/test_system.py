"""
Unit & Integration Test Script
==============================
Verifies sensor simulation, consecutive filtering, accident detection,
GPS simulation, emergency alert synthesis, and CSV logging.
"""

import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensor_simulator import SensorSimulator
from accident_detection import AccidentDetector
from gps_simulator import GPSSimulator
from alert_manager import AlertManager


def run_all_tests():
    print("=" * 65)
    print("RUNNING AUTOMATED UNIT TESTS FOR ACCIDENT DETECTION SYSTEM")
    print("=" * 65)

    # TEST 1: Normal Cruising
    print("\n[TEST 1] Testing Normal Cruising Telemetry & Detector Baseline...")
    sim = SensorSimulator()
    det = AccidentDetector(threshold_accel=25.0, consecutive_required=2)

    for i in range(5):
        reading = sim.get_reading()
        res = det.process_reading(reading['x'], reading['y'], reading['z'])
        print(f"  Sample {i+1}: X={reading['x']:5.2f}, Y={reading['y']:5.2f}, Z={reading['z']:5.2f} "
              f"-> Mag={res['magnitude']:5.2f} m/s^2 | Status={res['status']}")
        assert res['status'] == "NORMAL", f"Expected NORMAL, got {res['status']}"
    print("[OK] Test 1 Passed: Normal cruising telemetry generates safe baseline readings.")

    # TEST 2: Speed Bump (Single sample spike filter test)
    print("\n[TEST 2] Testing Road Bump Rejection (Digital Filter Test)...")
    sim.force_bump()
    bump_reading = sim.get_reading()
    bump_res = det.process_reading(bump_reading['x'], bump_reading['y'], bump_reading['z'])
    print(f"  Bump Sample: Mag={bump_res['magnitude']:.2f} m/s^2 | Status={bump_res['status']}")
    assert bump_res['status'] == "WARNING", f"Single spike should produce WARNING, got {bump_res['status']}"

    # Immediately following reading is normal:
    post_bump = sim.get_reading()
    post_res = det.process_reading(post_bump['x'], post_bump['y'], post_bump['z'])
    print(f"  Post-Bump Sample: Mag={post_res['magnitude']:.2f} m/s^2 | Status={post_res['status']}")
    assert post_res['status'] == "NORMAL", "Status should return to NORMAL after single spike."
    print("[OK] Test 2 Passed: Single-sample road bumps do NOT trigger false accident alarms.")

    # TEST 3: Sustained Collision Impact
    print("\n[TEST 3] Testing Sustained Collision Detection (2-Stage Verification)...")
    sim.force_accident(duration_frames=3)
    frame1 = sim.get_reading()
    res1 = det.process_reading(frame1['x'], frame1['y'], frame1['z'])
    print(f"  Crash Frame 1: Mag={res1['magnitude']:.2f} m/s^2 | Status={res1['status']}")
    assert res1['status'] in ("WARNING", "ACCIDENT_DETECTED")

    frame2 = sim.get_reading()
    res2 = det.process_reading(frame2['x'], frame2['y'], frame2['z'])
    print(f"  Crash Frame 2: Mag={res2['magnitude']:.2f} m/s^2 | Status={res2['status']} "
          f"| New Accident Event: {res2['is_new_accident']}")
    assert res2['status'] == "ACCIDENT_DETECTED", "Sustained high impact must trigger ACCIDENT_DETECTED."
    assert res2['is_new_accident'] is True, "Second consecutive high reading must flag new accident."
    print("[OK] Test 3 Passed: Consecutive high deceleration triggers confirmed accident status.")

    # TEST 4: GPS Simulation & Coordinates
    print("\n[TEST 4] Testing GPS Simulation & Google Maps Link...")
    gps = GPSSimulator(base_lat=12.971598, base_lon=77.594566)
    loc1 = gps.update_location()
    print(f"  Lat: {loc1['latitude']} deg N, Lon: {loc1['longitude']} deg E, Speed: {loc1['speed_kmh']} km/h")
    print(f"  Maps Link: {loc1['maps_url']}")
    assert "https://www.google.com/maps?q=" in loc1['maps_url']
    assert loc1['latitude'] > 0 and loc1['longitude'] > 0

    gps.freeze_location()
    loc2 = gps.update_location()
    assert loc2['speed_kmh'] == 0.0, "Speed should be 0.0 when location is frozen."
    print("[OK] Test 4 Passed: GPS coordinates dynamically generated and freeze properly on accident.")

    # TEST 5: Alert Generation & CSV History Logging
    print("\n[TEST 5] Testing Alert Message Synthesis & CSV History Storage...")
    test_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test_accident_history.csv")
    alert_mgr = AlertManager(history_file_path=test_csv)
    alert_mgr.clear_history()

    msg = alert_mgr.generate_alert_message(
        magnitude=res2['magnitude'],
        latitude=loc1['latitude'],
        longitude=loc1['longitude'],
        maps_url=loc1['maps_url']
    )
    print("  Alert Message generated (length: " + str(len(msg)) + " chars)")

    alert_mgr.log_accident_event(
        magnitude=res2['magnitude'],
        latitude=loc1['latitude'],
        longitude=loc1['longitude'],
        maps_url=loc1['maps_url']
    )
    history = alert_mgr.load_history()
    assert len(history) == 1, f"Expected 1 history record, found {len(history)}"
    print(f"  History record verified in CSV: {history[0]['Status']} at {history[0]['Timestamp']}")

    # Clean up test CSV
    if os.path.exists(test_csv):
        os.remove(test_csv)
    print("[OK] Test 5 Passed: Emergency alert synthesized and stored in CSV successfully.")

    print("\n" + "=" * 65)
    print("ALL 5 SYSTEM TESTS PASSED SUCCESSFULLY! (100% SUCCESS)")
    print("=" * 65)


if __name__ == "__main__":
    run_all_tests()
