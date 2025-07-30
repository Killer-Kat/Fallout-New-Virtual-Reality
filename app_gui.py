import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import datetime
import json
import os
from tracker_logic import TrackerLogic

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class FNVRTrackerGUI:
    """GUI for Fallout New Virtual Reality Tracker"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fallout: New Virtual Reality Tracker")
        self.root.geometry("600x550")
        self.root.resizable(True, True)
        
        # Preferences file path
        self.prefs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preferences.json')
        self.preferences = self.load_preferences()
        
        # Status queue for thread-safe updates
        self.status_queue = queue.Queue()
        
        # Tracker instance
        self.tracker = TrackerLogic(status_callback=self.queue_status_update)
        
        # Override paths if saved in preferences
        if 'ini_path' in self.preferences and self.preferences['ini_path']:
            self.tracker.config_variables['file_path'] = self.preferences['ini_path']
        if 'mmap_path' in self.preferences and self.preferences['mmap_path']:
            self.tracker.config_variables['mmap_file_path'] = self.preferences['mmap_path']
            # Reinitialize communication with new path
            self.tracker.setup_communication()
        
        # Setup UI
        self.setup_ui()
        
        # Start status update loop
        self.update_status_display()
        
    def load_preferences(self):
        """Load user preferences from JSON file"""
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_preferences(self):
        """Save user preferences to JSON file"""
        try:
            with open(self.prefs_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            self.add_log(f"Preferences could not be saved: {e}", "error")
        
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        scrollable = ScrollableFrame(self.root)
        scrollable.pack(fill="both", expand=True)
        main_frame = scrollable.scrollable_frame
        main_frame.configure(padding="10")  # add your padding here
        
        # Title
        title_label = ttk.Label(main_frame, text="FNVR Tracker Control Panel", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # INI File Path frame
        ini_frame = ttk.LabelFrame(main_frame, text="INI File Path", padding="10")
        ini_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # INI path display
        self.ini_path_var = tk.StringVar(value=self.tracker.config_variables.get('file_path', 'Not selected'))
        ini_path_label = ttk.Label(ini_frame, textvariable=self.ini_path_var, font=('Consolas', 9))
        ini_path_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        # Browse button
        browse_button = ttk.Button(ini_frame, text="Browse...", command=self.browse_ini_file)
        browse_button.grid(row=0, column=1, padx=5)
        
        # Configure grid
        ini_frame.columnconfigure(0, weight=1)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Status labels
        self.status_labels = {}
        status_items = [
            ("Status", "status"),
            ("SteamVR", "steamvr"),
            ("Controller", "controller"),
            ("Tracking", "tracking")
        ]
        
        for i, (label_text, key) in enumerate(status_items):
            ttk.Label(status_frame, text=f"{label_text}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            status_label = ttk.Label(status_frame, text="Waiting", foreground="gray")
            status_label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.status_labels[key] = status_label
            
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Start button
        self.start_button = ttk.Button(
            button_frame, 
            text="Start", 
            command=self.start_tracking,
            style="Accent.TButton"
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Stop button
        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop", 
            command=self.stop_tracking,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            width=70, 
            height=12,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure log text tags for different message types
        self.log_text.tag_config('info', foreground='black')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        
        # Hand selection frame
        hand_frame = ttk.LabelFrame(main_frame, text="Hand Pick", padding="10")
        hand_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Dual hand mode checkbox
        self.dual_hand_var = tk.BooleanVar(value=self.tracker.config_variables.get('dual_hand_enabled', False))
        dual_hand_checkbox = ttk.Checkbutton(
            hand_frame,
            text="Enable Two-Handed Mode",
            variable=self.dual_hand_var,
            command=self.on_dual_hand_toggle
        )
        dual_hand_checkbox.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Hand selection radio buttons
        self.active_hand_var = tk.StringVar(value=self.tracker.config_variables.get('default_hand', 'right'))
        ttk.Label(hand_frame, text="Active Hand:").grid(row=1, column=0, sticky=tk.W, padx=5)
        
        right_radio = ttk.Radiobutton(
            hand_frame,
            text="Right Hand",
            variable=self.active_hand_var,
            value="right",
            command=self.on_hand_change
        )
        right_radio.grid(row=1, column=1, padx=5)
        
        left_radio = ttk.Radiobutton(
            hand_frame,
            text="Left Hand",
            variable=self.active_hand_var,
            value="left",
            command=self.on_hand_change
        )
        left_radio.grid(row=1, column=2, padx=5)
        
        # Two-handed weapon checkbox
        self.two_handed_var = tk.BooleanVar(value=self.tracker.config_variables.get('two_handed_weapon_mode', False))
        self.two_handed_checkbox = ttk.Checkbutton(
            hand_frame,
            text="Two-Handed Weapon Mode",
            variable=self.two_handed_var,
            command=self.on_two_handed_toggle
        )
        self.two_handed_checkbox.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Set initial state based on dual hand mode
        if not self.dual_hand_var.get():
            self.two_handed_checkbox.config(state="disabled")
        
        # Smoothing controls frame
        smoothing_frame = ttk.LabelFrame(main_frame, text="Smoothing Settings", padding="10")
        smoothing_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Smoothing enabled checkbox
        self.smoothing_enabled_var = tk.BooleanVar(value=self.tracker.config_variables.get('smoothing_enabled', True))
        smoothing_checkbox = ttk.Checkbutton(
            smoothing_frame,
            text="Enable Data Smoothing",
            variable=self.smoothing_enabled_var,
            command=self.on_smoothing_toggle
        )
        smoothing_checkbox.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Smoothing strength slider
        ttk.Label(smoothing_frame, text="Softening Power:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.smoothing_strength_var = tk.DoubleVar(value=self.tracker.config_variables.get('position_min_cutoff', 1.0))
        smoothing_slider = ttk.Scale(
            smoothing_frame,
            from_=0.1,
            to=5.0,
            variable=self.smoothing_strength_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.on_smoothing_strength_change
        )
        smoothing_slider.grid(row=1, column=1, padx=5)
        
        # Smoothing value label
        self.smoothing_value_label = ttk.Label(smoothing_frame, text=f"{self.smoothing_strength_var.get():.1f}")
        self.smoothing_value_label.grid(row=1, column=2, padx=5)
        
        # Footer
        footer_label = ttk.Label(
            main_frame, 
            text="Fallout: New Virtual Reality - VR Motion Control", 
            font=('Arial', 8)
        )
        footer_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
    def queue_status_update(self, message, level="info"):
        """Queue a status update from the tracker thread"""
        self.status_queue.put((message, level))
        
    def update_status_display(self):
        """Process queued status updates"""
        try:
            while True:
                message, level = self.status_queue.get_nowait()
                self.add_log(message, level)
                self.update_status_labels(message, level)
        except queue.Empty:
            pass
            
        # Schedule next update
        self.root.after(100, self.update_status_display)
        
    def add_log(self, message, level="info"):
        """Add a message to the log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)
        
    def update_status_labels(self, message, level):
        """Update status labels based on messages"""
        message_lower = message.lower()
        
        if "openvr initialized" in message_lower:
            self.status_labels["steamvr"].config(text="Connected", foreground="green")
            self.status_labels["status"].config(text="Ready", foreground="green")
        elif "openvr init failed" in message_lower:
            self.status_labels["steamvr"].config(text="Could not connect", foreground="red")
            self.status_labels["status"].config(text="Error", foreground="red")
        elif "tracking started" in message_lower:
            self.status_labels["tracking"].config(text="Active", foreground="green")
            self.status_labels["status"].config(text="success", foreground="green")
        elif "tracking stopped" in message_lower:
            self.status_labels["tracking"].config(text="Stopped", foreground="gray")
            self.status_labels["status"].config(text="Stopped", foreground="gray")
        elif "hmd not connected" in message_lower:
            self.status_labels["controller"].config(text="No HMD", foreground="orange")
        elif "tracking active" in message_lower:
            self.status_labels["controller"].config(text="Being Tracked", foreground="green")
        elif "controller found at index" in message_lower:
            # Extract controller index from message
            import re
            match = re.search(r'index (\d+)', message)
            if match:
                index = match.group(1)
                self.status_labels["controller"].config(text=f"Controler {index} Connected", foreground="green")
            else:
                self.status_labels["controller"].config(text="Controler Found", foreground="green")
        elif "controller not found" in message_lower:
            self.status_labels["controller"].config(text="Controler Not Found", foreground="orange")
        elif "controller disconnected" in message_lower:
            self.status_labels["controller"].config(text="Controler Disconnected", foreground="red")
        elif "configuration loaded" in message_lower:
            self.status_labels["status"].config(text="Configuration Loaded", foreground="blue")
        elif "error" in message_lower or level == "error":
            self.status_labels["status"].config(text="Error", foreground="red")
        elif "config file not found" in message_lower:
            self.status_labels["status"].config(text="No Config (Default)", foreground="orange")
        elif "mmap communication initialized" in message_lower:
            self.status_labels["status"].config(text="MMAP Active", foreground="green")
        elif "mmap performance" in message_lower:
            # Show performance info in log
            pass
        elif "mmap failed" in message_lower:
            if "falling back" in message_lower:
                self.status_labels["status"].config(text="MMAP Failed (INI)", foreground="orange")
            else:
                self.status_labels["status"].config(text="MMAP Failed", foreground="red")
        elif "using ini file communication" in message_lower:
            self.status_labels["status"].config(text="INI Mode", foreground="blue")
            
    def start_tracking(self):
        """Start VR tracking"""
        self.add_log("Starting tracking...", "info")
        
        # Initialize VR
        if self.tracker.init_vr():
            # Start tracking
            self.tracker.start_tracking()
            
            # Update button states
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.add_log("VR failed to initialize. Make sure SteamVR is open.", "error")
            
    def stop_tracking(self):
        """Stop VR tracking"""
        self.add_log("Tracking is stopped...", "info")
        
        # Stop tracking
        self.tracker.stop_tracking()
        
        # Shutdown VR
        self.tracker.shutdown_vr()
        
        # Update button states
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Reset status labels
        self.status_labels["steamvr"].config(text="Not Connected", foreground="gray")
        self.status_labels["controller"].config(text="Waiting", foreground="gray")
        self.status_labels["tracking"].config(text="Passive", foreground="gray")
        
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
        
    def on_close(self):
        """Handle window closing event"""
        # Stop tracking if running
        if self.tracker.running:
            self.stop_tracking()
            
        # Destroy window
        self.root.destroy()
        
    def browse_ini_file(self):
        """Open file dialog to select INI file"""
        # Start from Steam common folder if it exists
        initial_dir = "C:/Program Files (x86)/Steam/steamapps/common"
        if not os.path.exists(initial_dir):
            initial_dir = "C:/"
            
        filename = filedialog.askopenfilename(
            title="Select Fallout New Vegas INI File",
            initialdir=initial_dir,
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")]
        )
        
        if filename:
            # Update tracker config
            self.tracker.config_variables['file_path'] = filename
            
            # Update display
            self.ini_path_var.set(filename)
            
            # Save to preferences
            self.preferences['ini_path'] = filename
            self.save_preferences()
            
            self.add_log(f"INI file path updated: {filename}", "success")
            
    def on_smoothing_toggle(self):
        """Handle smoothing enable/disable toggle"""
        enabled = self.smoothing_enabled_var.get()
        self.tracker.config_variables['smoothing_enabled'] = enabled
        
        # Reinitialize smoothing
        self.tracker.setup_smoothing()
        
        # Save preference
        self.preferences['smoothing_enabled'] = enabled
        self.save_preferences()
        
        status = "activated" if enabled else "disabled"
        self.add_log(f"Data smoothing {status}", "info")
        
    def on_smoothing_strength_change(self, value):
        """Handle smoothing strength slider change"""
        strength = float(value)
        self.smoothing_value_label.config(text=f"{strength:.1f}")
        
        # Update tracker configuration
        self.tracker.config_variables['position_min_cutoff'] = 5.1 - strength  # Inverse for intuitive control
        
        # Reinitialize smoothing if enabled
        if self.tracker.config_variables.get('smoothing_enabled', True):
            self.tracker.setup_smoothing()
            
        # Save preference
        self.preferences['smoothing_strength'] = strength
        self.save_preferences()
        
    def on_dual_hand_toggle(self):
        """Handle dual hand mode toggle"""
        enabled = self.dual_hand_var.get()
        self.tracker.config_variables['dual_hand_enabled'] = enabled
        self.tracker.dual_hand_mode = enabled
        
        # Enable/disable two-handed weapon checkbox based on dual hand mode
        if enabled:
            self.two_handed_checkbox.config(state="normal")
        else:
            self.two_handed_checkbox.config(state="disabled")
            self.two_handed_var.set(False)
            self.tracker.config_variables['two_handed_weapon_mode'] = False
        
        # Save preference
        self.preferences['dual_hand_enabled'] = enabled
        self.save_preferences()
        
        status = "activated" if enabled else "disabled"
        self.add_log(f"Two-handed mode {status}", "info")
        
    def on_hand_change(self):
        """Handle active hand selection change"""
        active_hand = self.active_hand_var.get()
        self.tracker.config_variables['default_hand'] = active_hand
        self.tracker.active_hand = active_hand
        
        # Save preference
        self.preferences['default_hand'] = active_hand
        self.save_preferences()
        
        hand_name = "Right Hand" if active_hand == "right" else "Left Hand"
        self.add_log(f"Active hand changed: {hand_name}", "info")
        
    def on_two_handed_toggle(self):
        """Handle two-handed weapon mode toggle"""
        enabled = self.two_handed_var.get()
        self.tracker.config_variables['two_handed_weapon_mode'] = enabled
        
        # Save preference
        self.preferences['two_handed_weapon_mode'] = enabled
        self.save_preferences()
        
        status = "activated" if enabled else "disabled"
        self.add_log(f"Two-handed weapon mode {status}", "info")


if __name__ == "__main__":
    app = FNVRTrackerGUI()
    app.run()