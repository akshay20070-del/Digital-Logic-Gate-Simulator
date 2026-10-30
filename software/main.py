"""
Smart Accident Detection and Emergency Alert System
===================================================
ECE Mini-Project - Software Simulation Application

Features:
- Real-time 3-axis acceleration telemetry simulation (X, Y, Z).
- Vector magnitude calculation: A = sqrt(X^2 + Y^2 + Z^2).
- Digital signal processing filter with consecutive reading verification.
- Simulated GPS coordinate generator with Google Maps integration.
- Automated emergency dispatch alert composer.
- Persistent accident history logging in CSV format.
- Interactive Tkinter GUI dashboard with modern dark-blue theme.

Important Note:
---------------
This is strictly a SOFTWARE SIMULATION project designed for college mini-project
evaluations in Electronics & Communication Engineering (ECE). No physical hardware,
microcontrollers, or paid SMS APIs are used.
"""

import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure local imports work regardless of current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from sensor_simulator import SensorSimulator
from accident_detection import AccidentDetector
from gps_simulator import GPSSimulator
from alert_manager import AlertManager


class SmartAccidentDetectionApp:
    """
    Main Tkinter Graphical User Interface for the Smart Accident Detection System.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Accident Detection and Emergency Alert System")
        self.root.geometry("1060x780")
        self.root.minsize(980, 720)

        # Initialize Simulation Modules
        self.sensor_sim = SensorSimulator()
        self.detector = AccidentDetector(threshold_accel=25.0, consecutive_required=2)
        self.gps_sim = GPSSimulator(base_lat=12.971598, base_lon=77.594566)
        self.alert_mgr = AlertManager()

        # Monitoring Control State
        self.is_monitoring = False
        self.update_interval_ms = 400  # Telemetry refresh every 400ms
        self.sample_counter = 0

        # UI Color Palette (Professional Dark Blue & Clean High-Contrast Cards)
        self.C_BG = "#0f172a"          # Deep Slate / Dark Blue Background
        self.C_NAV = "#1e293b"         # Dark Navy for Header & Navigation
        self.C_CARD = "#1e293b"        # Card background
        self.C_CARD_BORDER = "#334155" # Card borders
        self.C_TEXT = "#f8fafc"        # Crisp White Text
        self.C_MUTED = "#94a3b8"       # Secondary text
        self.C_ACCENT = "#38bdf8"      # Light Blue Accent
        
        # Status Colors
        self.C_NORMAL = "#10b981"      # Emerald Green
        self.C_WARNING = "#f59e0b"     # Amber / Yellow
        self.C_DANGER = "#ef4444"      # Crimson Red

        self.root.configure(bg=self.C_BG)

        # Build User Interface
        self._setup_styles()
        self._build_header()
        self._build_main_dashboard()
        self._build_status_bar()

        # Populate existing accident history
        self._refresh_history_table()

    def _setup_styles(self):
        """Configure ttk theme and custom styles."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        # Treeview styling
        self.style.configure(
            "Treeview",
            background="#1e293b",
            foreground="#f8fafc",
            rowheight=26,
            fieldbackground="#1e293b",
            borderwidth=0,
            font=("Segoe UI", 9)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#0f172a",
            foreground="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", "#0284c7")])

    def _build_header(self):
        """Build top navigation and project title header."""
        header_frame = tk.Frame(self.root, bg=self.C_NAV, height=75, padx=20, pady=12)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="SMART ACCIDENT DETECTION & EMERGENCY ALERT SYSTEM",
            font=("Segoe UI", 16, "bold"),
            fg=self.C_TEXT,
            bg=self.C_NAV
        )
        title_label.pack(anchor="w")

        subtitle_frame = tk.Frame(header_frame, bg=self.C_NAV)
        subtitle_frame.pack(fill=tk.X, pady=(2, 0))

        sub_label = tk.Label(
            subtitle_frame,
            text="ECE College Mini-Project | Software Simulation & Real-Time Impact Telemetry",
            font=("Segoe UI", 9),
            fg=self.C_MUTED,
            bg=self.C_NAV
        )
        sub_label.pack(side=tk.LEFT)

        disclaimer_tag = tk.Label(
            subtitle_frame,
            text="[SOFTWARE-ONLY SIMULATION • NO PHYSICAL SENSORS]",
            font=("Segoe UI", 9, "bold"),
            fg="#fbbf24",
            bg=self.C_NAV
        )
        disclaimer_tag.pack(side=tk.RIGHT)

    def _build_main_dashboard(self):
        """Construct the split dashboard with telemetry, GPS, and alerts."""
        container = tk.Frame(self.root, bg=self.C_BG, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Left Column: Telemetry & Controls (Width 52%)
        left_col = tk.Frame(container, bg=self.C_BG)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right Column: Emergency Alerts & History (Width 48%)
        right_col = tk.Frame(container, bg=self.C_BG)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # ------------------- LEFT COLUMN COMPONENTS -------------------
        # 1. Primary Status Banner
        self.status_banner = tk.Frame(left_col, bg=self.C_NORMAL, pady=12, padx=15)
        self.status_banner.pack(fill=tk.X, pady=(0, 12))

        self.status_title_label = tk.Label(
            self.status_banner,
            text="VEHICLE STATUS: MONITORING IDLE",
            font=("Segoe UI", 14, "bold"),
            fg="#ffffff",
            bg=self.C_NORMAL
        )
        self.status_title_label.pack()

        self.status_sub_label = tk.Label(
            self.status_banner,
            text="Click 'Start Monitoring' to initiate simulated vehicle telemetry.",
            font=("Segoe UI", 9),
            fg="#ffffff",
            bg=self.C_NORMAL
        )
        self.status_sub_label.pack(pady=(2, 0))

        # 2. Live Acceleration Telemetry Card
        telem_card = tk.LabelFrame(
            left_col,
            text=" Live Sensor Telemetry (Simulated Accelerometer) ",
            font=("Segoe UI", 10, "bold"),
            fg=self.C_ACCENT,
            bg=self.C_CARD,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        telem_card.pack(fill=tk.X, pady=(0, 12))

        # 3-Axis Readouts Grid
        axes_grid = tk.Frame(telem_card, bg=self.C_CARD)
        axes_grid.pack(fill=tk.X, pady=(0, 8))

        # X-Axis Box
        x_box = tk.Frame(axes_grid, bg="#0f172a", bd=1, relief="ridge", padx=10, pady=6)
        x_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(x_box, text="X-Axis (Lateral)", font=("Segoe UI", 8), fg=self.C_MUTED, bg="#0f172a").pack()
        self.lbl_x = tk.Label(x_box, text="0.00 m/s²", font=("Consolas", 13, "bold"), fg="#38bdf8", bg="#0f172a")
        self.lbl_x.pack()

        # Y-Axis Box
        y_box = tk.Frame(axes_grid, bg="#0f172a", bd=1, relief="ridge", padx=10, pady=6)
        y_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(y_box, text="Y-Axis (Longitudinal)", font=("Segoe UI", 8), fg=self.C_MUTED, bg="#0f172a").pack()
        self.lbl_y = tk.Label(y_box, text="0.00 m/s²", font=("Consolas", 13, "bold"), fg="#38bdf8", bg="#0f172a")
        self.lbl_y.pack()

        # Z-Axis Box
        z_box = tk.Frame(axes_grid, bg="#0f172a", bd=1, relief="ridge", padx=10, pady=6)
        z_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(z_box, text="Z-Axis (Vertical)", font=("Segoe UI", 8), fg=self.C_MUTED, bg="#0f172a").pack()
        self.lbl_z = tk.Label(z_box, text="9.81 m/s²", font=("Consolas", 13, "bold"), fg="#38bdf8", bg="#0f172a")
        self.lbl_z.pack()

        # Total Magnitude Display
        mag_frame = tk.Frame(telem_card, bg=self.C_CARD, pady=4)
        mag_frame.pack(fill=tk.X)

        tk.Label(
            mag_frame,
            text="Total Acceleration Magnitude A = √(X² + Y² + Z²):",
            font=("Segoe UI", 9),
            fg=self.C_TEXT,
            bg=self.C_CARD
        ).pack(side=tk.LEFT)

        self.lbl_mag = tk.Label(
            mag_frame,
            text="9.81 m/s² (1.00 g)",
            font=("Segoe UI", 12, "bold"),
            fg=self.C_NORMAL,
            bg=self.C_CARD
        )
        self.lbl_mag.pack(side=tk.RIGHT)

        # Dynamic Graphic Level Meter
        self.meter_canvas = tk.Canvas(telem_card, height=18, bg="#0f172a", highlightthickness=0)
        self.meter_canvas.pack(fill=tk.X, pady=(6, 4))
        self._update_meter(9.81)

        # Threshold Control
        thresh_frame = tk.Frame(telem_card, bg=self.C_CARD, pady=4)
        thresh_frame.pack(fill=tk.X)
        tk.Label(
            thresh_frame,
            text="Accident Threshold (m/s²):",
            font=("Segoe UI", 9),
            fg=self.C_MUTED,
            bg=self.C_CARD
        ).pack(side=tk.LEFT)

        self.thresh_spinbox = tk.Spinbox(
            thresh_frame,
            from_=15.0,
            to=60.0,
            increment=1.0,
            width=6,
            font=("Segoe UI", 9),
            command=self._on_threshold_change
        )
        self.thresh_spinbox.delete(0, "end")
        self.thresh_spinbox.insert(0, "25.0")
        self.thresh_spinbox.pack(side=tk.LEFT, padx=(8, 0))

        self.lbl_consec_info = tk.Label(
            thresh_frame,
            text="Consecutive Samples Required: 2",
            font=("Segoe UI", 8, "italic"),
            fg=self.C_MUTED,
            bg=self.C_CARD
        )
        self.lbl_consec_info.pack(side=tk.RIGHT)

        # 3. Simulated GPS Card
        gps_card = tk.LabelFrame(
            left_col,
            text=" Simulated GPS Location & Geonavigation ",
            font=("Segoe UI", 10, "bold"),
            fg=self.C_ACCENT,
            bg=self.C_CARD,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        gps_card.pack(fill=tk.X, pady=(0, 12))

        gps_grid = tk.Frame(gps_card, bg=self.C_CARD)
        gps_grid.pack(fill=tk.X)

        self.lbl_lat = tk.Label(
            gps_grid,
            text="Latitude:  12.971598° N",
            font=("Consolas", 10),
            fg=self.C_TEXT,
            bg=self.C_CARD
        )
        self.lbl_lat.grid(row=0, column=0, sticky="w", pady=2)

        self.lbl_lon = tk.Label(
            gps_grid,
            text="Longitude: 77.594566° E",
            font=("Consolas", 10),
            fg=self.C_TEXT,
            bg=self.C_CARD
        )
        self.lbl_lon.grid(row=1, column=0, sticky="w", pady=2)

        self.lbl_speed = tk.Label(
            gps_grid,
            text="Speed: 0.0 km/h",
            font=("Consolas", 10),
            fg=self.C_TEXT,
            bg=self.C_CARD
        )
        self.lbl_speed.grid(row=0, column=1, sticky="w", padx=(25, 0), pady=2)

        self.lbl_gps_status = tk.Label(
            gps_grid,
            text="Status: Active Track",
            font=("Consolas", 10),
            fg=self.C_NORMAL,
            bg=self.C_CARD
        )
        self.lbl_gps_status.grid(row=1, column=1, sticky="w", padx=(25, 0), pady=2)

        # Interactive Map Action Bar
        map_btn_frame = tk.Frame(gps_card, bg=self.C_CARD, pady=6)
        map_btn_frame.pack(fill=tk.X)

        self.btn_open_map = tk.Button(
            map_btn_frame,
            text="🌐 Open Location in Google Maps",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=4,
            command=self._open_google_maps
        )
        self.btn_open_map.pack(side=tk.LEFT)

        self.btn_copy_link = tk.Button(
            map_btn_frame,
            text="📋 Copy Coordinates Link",
            font=("Segoe UI", 9),
            bg="#334155",
            fg=self.C_TEXT,
            relief="flat",
            padx=10,
            pady=4,
            command=self._copy_maps_link
        )
        self.btn_copy_link.pack(side=tk.LEFT, padx=(10, 0))

        # 4. Control Panel Buttons
        btn_card = tk.LabelFrame(
            left_col,
            text=" System Operations & Control Panel ",
            font=("Segoe UI", 10, "bold"),
            fg=self.C_ACCENT,
            bg=self.C_CARD,
            bd=1,
            relief="solid",
            padx=12,
            pady=12
        )
        btn_card.pack(fill=tk.X)

        btn_grid = tk.Frame(btn_card, bg=self.C_CARD)
        btn_grid.pack(fill=tk.X)

        self.btn_start = tk.Button(
            btn_grid,
            text="▶ Start Monitoring",
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            command=self.start_monitoring
        )
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.btn_stop = tk.Button(
            btn_grid,
            text="⏹ Stop Monitoring",
            font=("Segoe UI", 10, "bold"),
            bg="#475569",
            fg="#ffffff",
            activebackground="#334155",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            state="disabled",
            command=self.stop_monitoring
        )
        self.btn_stop.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.btn_accident = tk.Button(
            btn_grid,
            text="💥 Simulate Accident",
            font=("Segoe UI", 10, "bold"),
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            command=self.simulate_accident
        )
        self.btn_accident.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.btn_reset = tk.Button(
            btn_grid,
            text="🔄 Reset System",
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            command=self.reset_system
        )
        self.btn_reset.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # ------------------- RIGHT COLUMN COMPONENTS -------------------
        # 1. Emergency Alert Dispatch Box
        alert_card = tk.LabelFrame(
            right_col,
            text=" Simulated Emergency Alert Message Dispatch ",
            font=("Segoe UI", 10, "bold"),
            fg=self.C_ACCENT,
            bg=self.C_CARD,
            bd=1,
            relief="solid",
            padx=10,
            pady=10
        )
        alert_card.pack(fill=tk.BOTH, expand=False, pady=(0, 12))

        self.txt_alert = tk.Text(
            alert_card,
            height=10,
            bg="#090d16",
            fg="#38bdf8",
            font=("Consolas", 8),
            bd=1,
            relief="solid",
            wrap=tk.WORD,
            padx=8,
            pady=8
        )
        self.txt_alert.pack(fill=tk.BOTH, expand=True)
        self.txt_alert.insert(
            "1.0",
            "Emergency dispatch idle.\n"
            "System will automatically synthesize a simulated distress dispatch\n"
            "upon detecting sustained impact exceeding threshold."
        )
        self.txt_alert.config(state="disabled")

        # 2. Accident History Table
        history_card = tk.LabelFrame(
            right_col,
            text=" Accident Incident History Log (CSV Storage) ",
            font=("Segoe UI", 10, "bold"),
            fg=self.C_ACCENT,
            bg=self.C_CARD,
            bd=1,
            relief="solid",
            padx=10,
            pady=10
        )
        history_card.pack(fill=tk.BOTH, expand=True)

        # Table Treeview
        columns = ("time", "mag", "status", "lat", "lon")
        self.tree = ttk.Treeview(history_card, columns=columns, show="headings", height=8)

        self.tree.heading("time", text="Timestamp")
        self.tree.heading("mag", text="Mag (m/s²)")
        self.tree.heading("status", text="Status")
        self.tree.heading("lat", text="Latitude")
        self.tree.heading("lon", text="Longitude")

        self.tree.column("time", width=130, anchor="center")
        self.tree.column("mag", width=85, anchor="center")
        self.tree.column("status", width=125, anchor="center")
        self.tree.column("lat", width=95, anchor="center")
        self.tree.column("lon", width=95, anchor="center")

        tree_scroll = ttk.Scrollbar(history_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # History Buttons
        hist_btn_frame = tk.Frame(history_card, bg=self.C_CARD, pady=6)
        hist_btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        btn_clear = tk.Button(
            hist_btn_frame,
            text="🗑 Clear Incident History",
            font=("Segoe UI", 8),
            bg="#ef4444",
            fg="#ffffff",
            relief="flat",
            padx=10,
            pady=4,
            command=self.clear_history
        )
        btn_clear.pack(side=tk.LEFT)

        btn_open_selected = tk.Button(
            hist_btn_frame,
            text="📍 Map Selected Event",
            font=("Segoe UI", 8),
            bg="#334155",
            fg=self.C_TEXT,
            relief="flat",
            padx=10,
            pady=4,
            command=self._map_selected_event
        )
        btn_open_selected.pack(side=tk.RIGHT)

    def _build_status_bar(self):
        """Build bottom footer bar for application status."""
        self.footer = tk.Frame(self.root, bg="#090d16", padx=15, pady=6)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_footer_status = tk.Label(
            self.footer,
            text="Status: Ready | Telemetry Rate: 2.5 Hz | Filter: 2-Stage Consecutive Verification",
            font=("Segoe UI", 8),
            fg=self.C_MUTED,
            bg="#090d16"
        )
        self.lbl_footer_status.pack(side=tk.LEFT)

        self.lbl_sample_info = tk.Label(
            self.footer,
            text="Samples Processed: 0",
            font=("Segoe UI", 8),
            fg=self.C_MUTED,
            bg="#090d16"
        )
        self.lbl_sample_info.pack(side=tk.RIGHT)

    def _update_meter(self, magnitude: float):
        """Draw dynamic graphic acceleration magnitude bar."""
        self.meter_canvas.delete("all")
        width = self.meter_canvas.winfo_width()
        if width <= 1:
            width = 440  # fallback initial width

        max_scale = 50.0  # full scale 50 m/s²
        ratio = min(1.0, max(0.0, magnitude / max_scale))
        meter_w = int(width * ratio)

        # Determine color based on level
        if magnitude < 18.0:
            fill_color = self.C_NORMAL
        elif magnitude < self.detector.threshold_accel:
            fill_color = self.C_WARNING
        else:
            fill_color = self.C_DANGER

        # Draw background track
        self.meter_canvas.create_rectangle(0, 0, width, 18, fill="#1e293b", width=0)
        # Draw active bar
        self.meter_canvas.create_rectangle(0, 0, meter_w, 18, fill=fill_color, width=0)
        # Draw threshold mark line
        thresh_x = int(width * (self.detector.threshold_accel / max_scale))
        self.meter_canvas.create_line(thresh_x, 0, thresh_x, 18, fill="#ffffff", width=2)

    def _on_threshold_change(self):
        """Callback when user modifies the threshold spinbox."""
        try:
            val = float(self.thresh_spinbox.get())
            self.detector.set_threshold(val)
        except ValueError:
            pass

    def start_monitoring(self):
        """Start the live telemetry simulation loop."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.btn_start.config(state="disabled", bg="#334155")
            self.btn_stop.config(state="normal", bg="#ef4444")
            self.lbl_footer_status.config(text="Status: Active Monitoring | Live Telemetry Streaming")
            self._simulation_step()

    def stop_monitoring(self):
        """Pause the telemetry loop."""
        self.is_monitoring = False
        self.btn_start.config(state="normal", bg="#16a34a")
        self.btn_stop.config(state="disabled", bg="#475569")
        self.lbl_footer_status.config(text="Status: Monitoring Paused")

    def simulate_accident(self):
        """Force a violent crash telemetry sequence."""
        self.sensor_sim.force_accident(duration_frames=3)
        if not self.is_monitoring:
            # Auto-start monitoring if stopped so user can see accident occur
            self.start_monitoring()

    def reset_system(self):
        """Reset sensor states, detector status, and telemetry labels."""
        self.sensor_sim.reset()
        self.detector.reset()
        self.gps_sim.reset()
        self.sample_counter = 0

        # Reset labels
        self.lbl_x.config(text="0.00 m/s²")
        self.lbl_y.config(text="0.00 m/s²")
        self.lbl_z.config(text="9.81 m/s²")
        self.lbl_mag.config(text="9.81 m/s² (1.00 g)", fg=self.C_NORMAL)
        self.lbl_speed.config(text="0.0 km/h")
        self.lbl_gps_status.config(text="Status: Reset to Base", fg=self.C_NORMAL)
        self._update_meter(9.81)

        # Reset banner
        self.status_banner.config(bg=self.C_NORMAL)
        self.status_title_label.config(text="VEHICLE STATUS: NORMAL OPERATION", bg=self.C_NORMAL)
        self.status_sub_label.config(text="System reset. Vehicle telemetry operating within safe limits.", bg=self.C_NORMAL)

        # Clear alert preview
        self.txt_alert.config(state="normal")
        self.txt_alert.delete("1.0", tk.END)
        self.txt_alert.insert("1.0", "System reset. Ready for telemetry monitoring.")
        self.txt_alert.config(state="disabled")

        self.lbl_sample_info.config(text="Samples Processed: 0")

    def _simulation_step(self):
        """Periodic telemetry step executing every update_interval_ms."""
        if not self.is_monitoring:
            return

        self.sample_counter += 1
        self.lbl_sample_info.config(text=f"Samples Processed: {self.sample_counter}")

        # 1. Fetch sensor reading
        reading = self.sensor_sim.get_reading()
        x, y, z = reading['x'], reading['y'], reading['z']

        # 2. Update GPS location
        gps_data = self.gps_sim.update_location()

        # 3. Process detection logic
        res = self.detector.process_reading(x, y, z)
        magnitude = res['magnitude']
        status = res['status']
        is_new_accident = res['is_new_accident']

        # 4. Update UI labels
        self.lbl_x.config(text=f"{x:.2f} m/s²")
        self.lbl_y.config(text=f"{y:.2f} m/s²")
        self.lbl_z.config(text=f"{z:.2f} m/s²")

        g_force = round(magnitude / 9.80665, 2)
        self.lbl_mag.config(text=f"{magnitude:.2f} m/s² ({g_force:.2f} g)")

        self.lbl_lat.config(text=f"Latitude:  {gps_data['latitude']:.6f}° N")
        self.lbl_lon.config(text=f"Longitude: {gps_data['longitude']:.6f}° E")
        self.lbl_speed.config(text=f"Speed: {gps_data['speed_kmh']:.1f} km/h")

        self._update_meter(magnitude)

        # 5. Handle Status Transitions
        if status == "ACCIDENT_DETECTED":
            self.status_banner.config(bg=self.C_DANGER)
            self.status_title_label.config(text="🚨 CRITICAL: VEHICLE ACCIDENT DETECTED! 🚨", bg=self.C_DANGER)
            self.status_sub_label.config(
                text=f"Impact force exceeded threshold ({magnitude:.2f} m/s²). Dispatching simulated alerts.",
                bg=self.C_DANGER
            )
            self.lbl_mag.config(fg=self.C_DANGER)
            self.lbl_gps_status.config(text="Status: CRASH POSITION FROZEN", fg=self.C_DANGER)
            self.gps_sim.freeze_location()

            if is_new_accident:
                self._handle_accident_event(magnitude, gps_data)

        elif status == "WARNING":
            self.status_banner.config(bg=self.C_WARNING)
            self.status_title_label.config(text="⚠️ WARNING: ELEVATED G-FORCE / ROAD ANOMALY", bg=self.C_WARNING)
            self.status_sub_label.config(
                text=f"High acceleration detected ({magnitude:.2f} m/s²). Filter checking consecutive samples...",
                bg=self.C_WARNING
            )
            self.lbl_mag.config(fg=self.C_WARNING)
            self.lbl_gps_status.config(text="Status: Active Track", fg=self.C_WARNING)

        else:  # NORMAL
            self.status_banner.config(bg=self.C_NORMAL)
            self.status_title_label.config(text="VEHICLE STATUS: NORMAL CRUISING", bg=self.C_NORMAL)
            self.status_sub_label.config(
                text="Acceleration within safe limits. No accident conditions detected.",
                bg=self.C_NORMAL
            )
            self.lbl_mag.config(fg=self.C_NORMAL)
            self.lbl_gps_status.config(text="Status: Active Track", fg=self.C_NORMAL)

        # Schedule next loop iteration
        self.root.after(self.update_interval_ms, self._simulation_step)

    def _handle_accident_event(self, magnitude: float, gps_data: dict):
        """Execute dispatch synthesis and log event to CSV history."""
        # Generate simulated SMS alert message
        alert_text = self.alert_mgr.generate_alert_message(
            magnitude=magnitude,
            latitude=gps_data['latitude'],
            longitude=gps_data['longitude'],
            maps_url=gps_data['maps_url']
        )

        # Display formatted message in text box
        self.txt_alert.config(state="normal")
        self.txt_alert.delete("1.0", tk.END)
        self.txt_alert.insert("1.0", alert_text)
        self.txt_alert.config(state="disabled")

        # Log into persistent CSV
        record = self.alert_mgr.log_accident_event(
            magnitude=magnitude,
            latitude=gps_data['latitude'],
            longitude=gps_data['longitude'],
            maps_url=gps_data['maps_url']
        )

        # Insert row into GUI table
        self.tree.insert(
            "",
            0,
            values=(
                record["Timestamp"],
                record["Acceleration_Magnitude_mps2"],
                record["Status"],
                record["Latitude"],
                record["Longitude"]
            )
        )

    def _refresh_history_table(self):
        """Load history from CSV into Treeview on launch."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        history = self.alert_mgr.load_history()
        for row in reversed(history):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row.get("Timestamp", "N/A"),
                    row.get("Acceleration_Magnitude_mps2", "N/A"),
                    row.get("Status", "N/A"),
                    row.get("Latitude", "N/A"),
                    row.get("Longitude", "N/A")
                )
            )

    def clear_history(self):
        """Clear historical CSV log and wipe Treeview."""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all accident records from CSV history?"):
            self.alert_mgr.clear_history()
            for item in self.tree.get_children():
                self.tree.delete(item)
            messagebox.showinfo("History Cleared", "Accident incident history has been cleared successfully.")

    def _open_google_maps(self):
        """Launch default web browser with current simulated GPS coordinates."""
        url = self.gps_sim.get_google_maps_link()
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Browser Error", f"Unable to open web browser: {e}")

    def _copy_maps_link(self):
        """Copy current Google Maps URL to system clipboard."""
        url = self.gps_sim.get_google_maps_link()
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        messagebox.showinfo("Copied", f"Simulated Google Maps link copied to clipboard:\n{url}")

    def _map_selected_event(self):
        """Open Google Maps for the selected event row in the Treeview."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an incident row from the history table first.")
            return

        values = self.tree.item(selected[0], "values")
        if len(values) >= 5:
            lat, lon = values[3], values[4]
            url = f"https://www.google.com/maps?q={lat},{lon}"
            try:
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("Browser Error", f"Unable to open web browser: {e}")


def main():
    """Application Entry Point."""
    root = tk.Tk()
    app = SmartAccidentDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
