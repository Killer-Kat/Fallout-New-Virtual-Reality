import math
import keyboard
import openvr
import time
import ctypes
import numpy as np
import configparser
import os
import threading
import logging
from datetime import datetime
from mmap_communication import MMAPCommunicator
from data_smoothing import TrackingSmoother
from gesture_recognition import GestureRecognizer


class TrackerLogic:
    """VR tracking logic separated from GUI"""
    
    def __init__(self, status_callback=None):
        self.vr_system = None
        self.config_variables = {}
        self.status_callback = status_callback
        self.running = False
        self.tracking_thread = None
        self.mmap_comm = None
        self.use_mmap = False
        self.smoother = None
        self.gesture_recognizer = None
        self.last_player_rotation = (0, 0, 0)  # Store for gesture callbacks
        
        # Dual controller support
        self.left_controller_index = None
        self.right_controller_index = None
        self.active_hand = "right"  # Default to right hand
        self.dual_hand_mode = False
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.load_config()
        
        # Setup communication method
        self.setup_communication()
        
        # Setup data smoothing
        self.setup_smoothing()
        
        # Setup gesture recognition
        self.setup_gesture_recognition()
        
        # Apply dual hand settings
        self.dual_hand_mode = self.config_variables.get('dual_hand_enabled', False)
        self.active_hand = self.config_variables.get('default_hand', 'right')
        
    def setup_logging(self):
        """Configure logging to file and optionally to console"""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, 'fnvr_tracker.log')
        
        # Configure logging format
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Create logger
        self.logger = logging.getLogger('FNVR_Tracker')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler - always log to file
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        self.logger.addHandler(file_handler)
        
        # Console handler - only if no GUI callback
        if not self.status_callback:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter(log_format, date_format))
            self.logger.addHandler(console_handler)
            
        self.logger.info("FNVR Tracker started")
        
    def load_config(self):
        """Load configuration from config.ini file"""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, 'config.ini')
            
            if not os.path.exists(config_path):
                self.update_status("Config file not found, using defaults", "warning")
                # Set default values
                self.set_default_config()
                return False
                
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Load all configuration values into a dictionary
            self.config_variables = {
                'file_path': config.get('paths', 'ini_file_path'),
                'x_scale': config.getfloat('position_scaling', 'x_scale'),
                'x_offset': config.getfloat('position_scaling', 'x_offset'),
                'y_scale': config.getfloat('position_scaling', 'y_scale'),
                'y_offset': config.getfloat('position_scaling', 'y_offset'),
                'z_scale': config.getfloat('position_scaling', 'z_scale'),
                'z_offset': config.getfloat('position_scaling', 'z_offset'),
                'xr_scale': config.getfloat('rotation_scaling', 'xr_scale'),
                'xr_offset': config.getfloat('rotation_scaling', 'xr_offset'),
                'yr_scale': config.getfloat('rotation_scaling', 'yr_scale'),
                'yr_offset': config.getfloat('rotation_scaling', 'yr_offset'),
                'zr_scale': config.getfloat('rotation_scaling', 'zr_scale'),
                'zr_offset': config.getfloat('rotation_scaling', 'zr_offset'),
                'pxr_scale': config.getfloat('player_rotation', 'pxr_scale'),
                'pxr_offset': config.getfloat('player_rotation', 'pxr_offset'),
                'pyr_scale': config.getfloat('player_rotation', 'pyr_scale'),
                'pyr_offset': config.getfloat('player_rotation', 'pyr_offset'),
                'pzr_scale': config.getfloat('player_rotation', 'pzr_scale'),
                'pzr_offset': config.getfloat('player_rotation', 'pzr_offset'),
                'pipboy_x': config.getfloat('pipboy_position', 'pipboy_x'),
                'pipboy_y': config.getfloat('pipboy_position', 'pipboy_y'),
                'pipboy_z': config.getfloat('pipboy_position', 'pipboy_z'),
                'pipboy_xr': config.getfloat('pipboy_position', 'pipboy_xr'),
                'pipboy_yr': config.getfloat('pipboy_position', 'pipboy_yr'),
                'pipboy_zr': config.getfloat('pipboy_position', 'pipboy_zr'),
                'gesture_x': config.getfloat('pipboy_gesture', 'gesture_x'),
                'gesture_y': config.getfloat('pipboy_gesture', 'gesture_y'),
                'gesture_z': config.getfloat('pipboy_gesture', 'gesture_z'),
                'gesture_threshold': config.getfloat('pipboy_gesture', 'gesture_threshold'),
                'pause_x': config.getfloat('pause_menu_gesture', 'pause_x'),
                'pause_y': config.getfloat('pause_menu_gesture', 'pause_y'),
                'pause_z': config.getfloat('pause_menu_gesture', 'pause_z'),
                'pause_threshold': config.getfloat('pause_menu_gesture', 'pause_threshold'),
                'loop_delay': config.getfloat('timing', 'loop_delay'),
                'tab_press_duration': config.getfloat('timing', 'tab_press_duration'),
                'escape_press_duration': config.getfloat('timing', 'escape_press_duration'),
                # Communication settings
                'comm_method': config.get('communication', 'method', fallback='ini'),
                'mmap_file_path': config.get('communication', 'mmap_file_path', fallback=''),
                'fallback_to_ini': config.getboolean('communication', 'fallback_to_ini', fallback=True),
                # Smoothing settings
                'smoothing_enabled': config.getboolean('smoothing', 'enabled', fallback=True),
                'smoothing_filter': config.get('smoothing', 'filter', fallback='one_euro'),
                'position_min_cutoff': config.getfloat('smoothing', 'position_min_cutoff', fallback=1.0),
                'position_beta': config.getfloat('smoothing', 'position_beta', fallback=0.007),
                'position_alpha': config.getfloat('smoothing', 'position_alpha', fallback=0.3),
                'position_window_size': config.getint('smoothing', 'position_window_size', fallback=5),
                'rotation_alpha': config.getfloat('smoothing', 'rotation_alpha', fallback=0.5),
                # Gesture recognition settings
                'gesture_recognition_enabled': config.getboolean('gesture_recognition', 'enabled', fallback=True),
                'gesture_dwell_time': config.getfloat('gesture_recognition', 'dwell_time', fallback=0.5),
                'gesture_cooldown': config.getfloat('gesture_recognition', 'cooldown', fallback=1.0),
                'gesture_max_velocity': config.getfloat('gesture_recognition', 'max_velocity', fallback=0.5),
                # Dual hand settings
                'dual_hand_enabled': config.getboolean('dual_hand', 'enabled', fallback=False),
                'default_hand': config.get('dual_hand', 'default_hand', fallback='right'),
                'left_x_scale': config.getfloat('dual_hand', 'left_x_scale', fallback=-50),
                'left_y_scale': config.getfloat('dual_hand', 'left_y_scale', fallback=50),
                'left_z_scale': config.getfloat('dual_hand', 'left_z_scale', fallback=50),
                'left_x_offset': config.getfloat('dual_hand', 'left_x_offset', fallback=-15),
                'left_y_offset': config.getfloat('dual_hand', 'left_y_offset', fallback=-10),
                'left_z_offset': config.getfloat('dual_hand', 'left_z_offset', fallback=0),
                'two_handed_weapon_mode': config.getboolean('dual_hand', 'two_handed_weapon_mode', fallback=False),
                'two_handed_min_distance': config.getfloat('dual_hand', 'two_handed_min_distance', fallback=0.2),
                'two_handed_max_distance': config.getfloat('dual_hand', 'two_handed_max_distance', fallback=0.8)
            }
            
            self.update_status("Configuration loaded", "info")
            return True
            
        except Exception as e:
            self.update_status(f"Config error: {e}", "error")
            self.logger.exception("Error loading configuration")
            # Set default values
            self.set_default_config()
            return False
            
    def set_default_config(self):
        """Set default configuration values"""
        self.config_variables = {
            'file_path': 'E:/SteamLibrary/steamapps/common/Fallout New Vegas/Data/Config/Meh.ini',
            'x_scale': 50, 'x_offset': 15,
            'y_scale': -50, 'y_offset': -10,
            'z_scale': -50, 'z_offset': 0,
            'xr_scale': -120, 'xr_offset': 10,
            'yr_scale': 0, 'yr_offset': 0,
            'zr_scale': 120, 'zr_offset': -75,
            'pxr_scale': 0, 'pxr_offset': 0,
            'pyr_scale': 0, 'pyr_offset': 0,
            'pzr_scale': -150, 'pzr_offset': -7.5,
            'pipboy_x': -0.1615, 'pipboy_y': -0.5, 'pipboy_z': 0.1281,
            'pipboy_xr': 0.0655, 'pipboy_yr': 0.041, 'pipboy_zr': 0.6291,
            'gesture_x': 0.12, 'gesture_y': 0.24, 'gesture_z': -0.29,
            'gesture_threshold': 0.1,
            'pause_x': -0.3158, 'pause_y': -0.1897, 'pause_z': -0.1316,
            'pause_threshold': 0.1,
            'loop_delay': 0.025,
            'tab_press_duration': 0.05,
            'escape_press_duration': 0.75
        }
        self.logger.info("Using default configuration values")
            
    def setup_communication(self):
        """Setup communication method (MMAP or INI)"""
        comm_method = self.config_variables.get('comm_method', 'ini').lower()
        
        if comm_method == 'mmap':
            mmap_path = self.config_variables.get('mmap_file_path', '')
            if not mmap_path:
                self.update_status("MMAP path not configured, using INI", "warning")
                self.use_mmap = False
                return
                
            # Create MMAP communicator
            self.mmap_comm = MMAPCommunicator(mmap_path, self.logger)
            if self.mmap_comm.initialize():
                self.use_mmap = True
                self.update_status("MMAP communication initialized", "success")
                
                # Run benchmark
                self.run_performance_benchmark()
            else:
                self.use_mmap = False
                if self.config_variables.get('fallback_to_ini', True):
                    self.update_status("MMAP failed, falling back to INI", "warning")
                else:
                    self.update_status("MMAP failed, no fallback", "error")
        else:
            self.use_mmap = False
            self.update_status("Using INI file communication", "info")
            
    def run_performance_benchmark(self):
        """Run a quick performance benchmark"""
        try:
            from mmap_communication import MMAPBenchmark
            ini_path = self.config_variables.get('file_path', 'test.ini')
            
            results = MMAPBenchmark.benchmark_write_speed(
                self.mmap_comm, 
                ini_path, 
                iterations=100
            )
            
            self.update_status(
                f"MMAP Performance: {results['mmap_avg_time_ms']:.3f}ms avg, "
                f"INI: {results['ini_avg_time_ms']:.3f}ms avg, "
                f"Speedup: {results['speedup_factor']:.1f}x",
                "info"
            )
        except Exception as e:
            self.logger.debug(f"Benchmark error: {e}")
            
    def setup_smoothing(self):
        """Setup data smoothing based on configuration"""
        if self.config_variables.get('smoothing_enabled', True):
            try:
                self.smoother = TrackingSmoother(self.config_variables, self.logger)
                self.update_status("Data smoothing enabled", "info")
                
                # Log smoothing configuration
                filter_type = self.config_variables.get('smoothing_filter', 'one_euro')
                self.logger.info(f"Using {filter_type} smoothing filter")
            except Exception as e:
                self.update_status(f"Smoothing setup failed: {e}", "error")
                self.logger.exception("Error setting up smoothing")
                self.smoother = None
        else:
            self.smoother = None
            self.update_status("Data smoothing disabled", "info")
            
    def setup_gesture_recognition(self):
        """Setup advanced gesture recognition"""
        if self.config_variables.get('gesture_recognition_enabled', True):
            try:
                self.gesture_recognizer = GestureRecognizer(self.config_variables, self.logger)
                
                # Register gesture callbacks
                self.gesture_recognizer.register_gesture_callback('pipboy', self.on_pipboy_gesture)
                self.gesture_recognizer.register_gesture_callback('pause', self.on_pause_gesture)
                
                self.update_status("Advanced gesture recognition enabled", "info")
            except Exception as e:
                self.update_status(f"Gesture recognition setup failed: {e}", "error")
                self.logger.exception("Error setting up gesture recognition")
                self.gesture_recognizer = None
        else:
            self.gesture_recognizer = None
            self.update_status("Gesture recognition disabled", "info")
            
    def on_pipboy_gesture(self):
        """Callback for pipboy gesture"""
        cfg = self.config_variables
        playerXr, playerYr, playerZr = self.last_player_rotation  # Store these values
        
        # Update to pipboy position
        self.update_tracking_data(
            cfg.get('pipboy_x', -0.1615), cfg.get('pipboy_y', -0.5), cfg.get('pipboy_z', 0.1281),
            cfg.get('pipboy_xr', 0.0655), cfg.get('pipboy_yr', 0.041), cfg.get('pipboy_zr', 0.6291),
            playerZr, playerYr, -playerXr
        )
        
        # Press Tab
        keyboard.press('Tab')
        time.sleep(cfg.get('tab_press_duration', 0.05))
        keyboard.release('Tab')
        
        # Update again to ensure position is held
        self.update_tracking_data(
            cfg.get('pipboy_x', -0.1615), cfg.get('pipboy_y', -0.5), cfg.get('pipboy_z', 0.1281),
            cfg.get('pipboy_xr', 0.0655), cfg.get('pipboy_yr', 0.041), cfg.get('pipboy_zr', 0.6291),
            playerZr, playerYr, -playerXr
        )
        
        self.update_status("Pipboy gesture triggered", "info")
        
    def on_pause_gesture(self):
        """Callback for pause menu gesture"""
        keyboard.press('Escape')
        time.sleep(self.config_variables.get('escape_press_duration', 0.75))
        keyboard.release('Escape')
        
        self.update_status("Pause menu gesture triggered", "info")
            
    def update_status(self, message, level="info"):
        """Send status update to callback if available and log it"""
        # Log the message
        if level == "info":
            self.logger.info(message)
        elif level == "success":
            self.logger.info(f"SUCCESS: {message}")
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.debug(message)
            
        # Send to callback if available
        if self.status_callback:
            self.status_callback(message, level)
        else:
            print(f"[{level.upper()}] {message}")
            
    def init_vr(self):
        """Initialize OpenVR connection"""
        try:
            self.vr_system = openvr.init(openvr.VRApplication_Background)
            self.update_status("OpenVR initialized", "success")
            return True
        except openvr.OpenVRError as e:
            error_msg = f"OpenVR init failed: {e}"
            self.update_status(error_msg, "error")
            self.logger.exception("OpenVR initialization error")
            return False
        except Exception as e:
            error_msg = f"Unexpected error initializing VR: {e}"
            self.update_status(error_msg, "error")
            self.logger.exception("Unexpected VR initialization error")
            return False
            
    def shutdown_vr(self):
        """Shutdown OpenVR connection"""
        if self.vr_system is not None:
            openvr.shutdown()
            self.vr_system = None
            self.update_status("OpenVR shutdown", "info")
            
        # Clean up MMAP if used
        if self.mmap_comm:
            self.mmap_comm.cleanup()
            self.mmap_comm = None
            
    def start_tracking(self):
        """Start tracking in a separate thread"""
        if not self.running:
            self.running = True
            self.tracking_thread = threading.Thread(target=self._tracking_loop)
            self.tracking_thread.daemon = True
            self.tracking_thread.start()
            self.update_status("Tracking started", "success")
            
    def stop_tracking(self):
        """Stop tracking"""
        self.running = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=2.0)
        self.update_status("Tracking stopped", "info")
        
    def update_tracking_data(self, iX, iY, iZ, iXr, iYr, iZr, pXr, pYr, pZr):
        """Update tracking data using configured communication method"""
        if self.use_mmap and self.mmap_comm:
            # Try MMAP first
            success = self.mmap_comm.write_tracking_data(
                iX, iY, iZ, iXr, iYr, iZr, pXr, pYr, pZr,
                self.config_variables
            )
            
            if not success and self.config_variables.get('fallback_to_ini', True):
                # Fallback to INI
                self.update_ini(iX, iY, iZ, iXr, iYr, iZr, pXr, pYr, pZr)
        else:
            # Use INI
            self.update_ini(iX, iY, iZ, iXr, iYr, iZr, pXr, pYr, pZr)
            
    def update_ini(self, iX, iY, iZ, iXr, iYr, iZr, pXr, pYr, pZr):
        """Update the game INI file with tracking data"""
        try:
            cfg = self.config_variables
            file_path = cfg.get('file_path', 'E:/SteamLibrary/steamapps/common/Fallout New Vegas/Data/Config/Meh.ini')
            
            with open(file_path, "w") as f:
                f.write("[Standard]\n")
                f.write(f'fCanIOpenThis = {1}\n')
                f.write(f"fiX = {(iX * cfg.get('x_scale', 50)) + cfg.get('x_offset', 15):.4f}\n")
                f.write(f"fiY = {(iY * cfg.get('y_scale', -50)) + cfg.get('y_offset', -10):.4f}\n")
                f.write(f"fiZ = {(iZ * cfg.get('z_scale', -50)) + cfg.get('z_offset', 0):.4f}\n")
                f.write(f"fiXr = {(iXr * cfg.get('xr_scale', -120)) + cfg.get('xr_offset', 10):.4f}\n")
                f.write(f"fiZr = {(iZr * cfg.get('zr_scale', 120)) + cfg.get('zr_offset', -75):.4f}\n")
                f.write(f"fpZr = {(pZr * cfg.get('pzr_scale', -150)) + cfg.get('pzr_offset', -7.5):.4f}\n")
        except FileNotFoundError:
            self.update_status(f"INI file not found: {file_path}", "error")
            self.logger.error(f"INI file not found at: {file_path}")
        except PermissionError:
            self.update_status(f"Permission denied writing to INI: {file_path}", "error")
            self.logger.error(f"Permission denied for INI file: {file_path}")
        except Exception as e:
            self.update_status(f"INI update error: {e}", "error")
            self.logger.exception("Unexpected error updating INI file")
            
    def calculate_distance_xyz(self, x1, y1, z1, x2, y2, z2):
        """Calculate 3D distance between two points"""
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        return distance
        
    def get_rotation(self, matrix):
        """Extract rotation quaternion from transformation matrix"""
        q = openvr.HmdQuaternion_t()
        q.w = np.sqrt(max(0, 1 + matrix[0][0] + matrix[1][1] + matrix[2][2])) / 2
        q.x = np.sqrt(max(0, 1 + matrix[0][0] - matrix[1][1] - matrix[2][2])) / 2
        q.y = np.sqrt(max(0, 1 - matrix[0][0] + matrix[1][1] - matrix[2][2])) / 2
        q.z = np.sqrt(max(0, 1 - matrix[0][0] - matrix[1][1] + matrix[2][2])) / 2
        q.x = np.copysign(q.x, matrix[2][1] - matrix[1][2])
        q.y = np.copysign(q.y, matrix[0][2] - matrix[2][0])
        q.z = np.copysign(q.z, matrix[1][0] - matrix[0][1])
        return q
        
    def quaternion_to_euler(self, q):
        """Convert quaternion (w, x, y, z) to Euler angles (roll, pitch, yaw) in degrees."""
        # roll (x-axis rotation)
        sinr_cosp = 2 * (q.w * q.x + q.y * q.z)
        cosr_cosp = 1 - 2 * (q.x * q.x + q.y * q.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # pitch (y-axis rotation)
        sinp = 2 * (q.w * q.y - q.z * q.x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)
            
        # yaw (z-axis rotation)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)
        
    def get_position(self, matrix):
        """Extract position vector from transformation matrix"""
        v = openvr.HmdVector3_t()
        v.v = (ctypes.c_float * 3)(matrix[0][3], matrix[1][3], matrix[2][3])
        return v
        
    def quaternion_conjugate(self, q):
        """Calculate quaternion conjugate"""
        return openvr.HmdQuaternion_t(q.w, -q.x, -q.y, -q.z)
        
    def quaternion_multiply(self, q1, q2):
        """Multiply two quaternions"""
        w = q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z
        x = q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y
        y = q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x
        z = q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w
        return openvr.HmdQuaternion_t(w, x, y, z)
        
    def rotate_vector_by_quaternion(self, vector, quaternion):
        """Rotate a vector by a quaternion"""
        pure_q_vector = openvr.HmdQuaternion_t(0, vector.v[0], vector.v[1], vector.v[2])
        quaternion_inverse = self.quaternion_conjugate(quaternion)
        rotated_q = self.quaternion_multiply(quaternion, self.quaternion_multiply(pure_q_vector, quaternion_inverse))
        rotated_vector = openvr.HmdVector3_t()
        rotated_vector.v = (ctypes.c_float * 3)(rotated_q.x, rotated_q.y, rotated_q.z)
        return rotated_vector
        
    def find_controller_indices(self):
        """Find indices of all active controllers"""
        controllers = []
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            device_class = self.vr_system.getTrackedDeviceClass(i)
            if device_class == openvr.TrackedDeviceClass_Controller:
                if self.vr_system.isTrackedDeviceConnected(i):
                    controllers.append(i)
        return controllers
        
    def get_controller_role(self, device_index):
        """Get the role (left/right) of a controller"""
        role = self.vr_system.getControllerRoleForTrackedDeviceIndex(device_index)
        if role == openvr.TrackedControllerRole_LeftHand:
            return "left"
        elif role == openvr.TrackedControllerRole_RightHand:
            return "right"
        else:
            return "unknown"
        
    def _tracking_loop(self):
        """Main tracking loop"""
        if self.vr_system is None:
            self.update_status("VR not initialized", "error")
            return
            
        hmd_index = openvr.k_unTrackedDeviceIndex_Hmd
        max_devices = openvr.k_unMaxTrackedDeviceCount
        TrackedDevicePose_t = openvr.TrackedDevicePose_t
        
        self.update_status("Tracking active", "success")
        
        while self.running:
            try:
                # Check if HMD is connected
                if not self.vr_system.isTrackedDeviceConnected(hmd_index):
                    self.update_status("HMD not connected", "warning")
                    time.sleep(1)
                    continue
                    
                # Find controllers
                controller_indices = self.find_controller_indices()
                if not controller_indices:
                    self.update_status("No controllers found", "warning")
                    time.sleep(1)
                    continue
                    
                # Identify left and right controllers
                self.left_controller_index = None
                self.right_controller_index = None
                
                for idx in controller_indices:
                    role = self.get_controller_role(idx)
                    if role == "left":
                        self.left_controller_index = idx
                    elif role == "right":
                        self.right_controller_index = idx
                        
                # Determine which controller to use
                active_controller_index = None
                if self.dual_hand_mode:
                    # In dual hand mode, we'll track both
                    if self.left_controller_index and self.right_controller_index:
                        self.update_status("Both controllers connected", "success")
                    else:
                        self.update_status("Dual hand mode requires both controllers", "warning")
                        time.sleep(1)
                        continue
                else:
                    # Single hand mode - use selected hand
                    if self.active_hand == "left" and self.left_controller_index:
                        active_controller_index = self.left_controller_index
                    elif self.active_hand == "right" and self.right_controller_index:
                        active_controller_index = self.right_controller_index
                    else:
                        # Fallback to any available controller
                        active_controller_index = controller_indices[0]
                        
                    if active_controller_index is None:
                        self.update_status(f"{self.active_hand} controller not found", "warning")
                        time.sleep(1)
                        continue
                    
                origin = openvr.TrackingUniverseStanding
                predicted_seconds = 0.0
                poses_array = (TrackedDevicePose_t * max_devices)()
                
                try:
                    returned_poses = self.vr_system.getDeviceToAbsoluteTrackingPose(
                        origin, predicted_seconds, poses_array
                    )
                except Exception as e:
                    self.update_status(f"Error getting tracking poses: {e}", "error")
                    self.logger.exception("Error in getDeviceToAbsoluteTrackingPose")
                    time.sleep(1)
                    continue
                
                if self.dual_hand_mode:
                    # Dual hand mode - process both controllers
                    if len(returned_poses) > max(hmd_index, self.left_controller_index, self.right_controller_index):
                        hmd_pose = returned_poses[hmd_index]
                        left_pose = returned_poses[self.left_controller_index]
                        right_pose = returned_poses[self.right_controller_index]
                        
                        if hmd_pose.bPoseIsValid and left_pose.bPoseIsValid and right_pose.bPoseIsValid:
                            # Process both hands
                            self._process_dual_hand_tracking(hmd_pose, left_pose, right_pose)
                        else:
                            self.update_status("Invalid pose data for dual hand mode", "warning")
                else:
                    # Single hand mode
                    if len(returned_poses) > max(hmd_index, active_controller_index):
                        hmd_pose = returned_poses[hmd_index]
                        con_pose = returned_poses[active_controller_index]
                    
                        if hmd_pose.bPoseIsValid and con_pose.bPoseIsValid:
                            m = hmd_pose.mDeviceToAbsoluteTracking
                            n = con_pose.mDeviceToAbsoluteTracking
                            
                            hmd_position_world = self.get_position(m)
                            con_position_world = self.get_position(n)
                            
                            hmd_matrix = [
                                [m[0][0], m[0][1], m[0][2], m[0][3]],
                                [m[1][0], m[1][1], m[1][2], m[1][3]],
                                [m[2][0], m[2][1], m[2][2], m[2][3]]
                            ]
                            hmd_rotation_world = self.get_rotation(hmd_matrix)
                            
                            con_matrix = [
                                [n[0][0], n[0][1], n[0][2], n[0][3]],
                                [n[1][0], n[1][1], n[1][2], n[1][3]],
                                [n[2][0], n[2][1], n[2][2], n[2][3]]
                            ]
                            con_rotation_world = self.get_rotation(con_matrix)
                            
                            world_diff_x = con_position_world.v[0] - hmd_position_world.v[0]
                            world_diff_y = con_position_world.v[1] - hmd_position_world.v[1]
                            world_diff_z = con_position_world.v[2] - hmd_position_world.v[2]
                            world_diff_vector = openvr.HmdVector3_t()
                            world_diff_vector.v = (ctypes.c_float * 3)(world_diff_x, world_diff_y, world_diff_z)
                            
                            hmd_rotation_inverse = self.quaternion_conjugate(hmd_rotation_world)
                            relative_position = self.rotate_vector_by_quaternion(world_diff_vector, hmd_rotation_inverse)
                            relative_rotation = self.quaternion_multiply(hmd_rotation_inverse, con_rotation_world)
                            
                            # Convert quaternions to Euler angles for game logic
                            hmd_roll, hmd_pitch, hmd_yaw = self.quaternion_to_euler(hmd_rotation_world)
                            rel_roll, rel_pitch, rel_yaw = self.quaternion_to_euler(relative_rotation)
                            
                            # InertiaController Bone Pose
                            inertiaZ, inertiaX, inertiaY = relative_position.v
                            inertiaXr, inertiaYr, inertiaZr = rel_roll, rel_pitch, rel_yaw
                            playerZr = hmd_yaw
                            
                            # Apply smoothing if enabled
                            if self.smoother:
                                # Smooth position
                                inertiaX, inertiaY, inertiaZ = self.smoother.smooth_position(
                                    inertiaX, inertiaY, inertiaZ
                                )
                                
                                # Smooth controller rotation (quaternion) before converting
                                smoothed_rot_quat = self.smoother.smooth_quaternion(
                                    relative_rotation.w, relative_rotation.x, 
                                    relative_rotation.y, relative_rotation.z
                                )
                                smoothed_relative_rotation = openvr.HmdQuaternion_t(*smoothed_rot_quat)
                                rel_roll, rel_pitch, rel_yaw = self.quaternion_to_euler(smoothed_relative_rotation)
                                
                                # Update inertia values with smoothed rotation
                                inertiaXr, inertiaYr, inertiaZr = rel_roll, rel_pitch, rel_yaw
                            
                            # Store player rotation for gesture callbacks
                            self.last_player_rotation = (hmd_roll, hmd_pitch, hmd_yaw)
                            
                            # Update tracking data with correct values
                            self.update_tracking_data(inertiaX, inertiaY, inertiaZ, inertiaXr, inertiaYr, inertiaZr, 0, 0, playerZr)
                            
                            # Update gesture recognition with smoothed position
                            if self.gesture_recognizer:
                                gesture_pos = (inertiaX, inertiaY, inertiaZ)
                                self.gesture_recognizer.update(gesture_pos)
                                
                        else:
                            self.update_status("Invalid pose data", "warning")
                    else:
                        self.update_status("Could not retrieve pose", "warning")
                    
                time.sleep(self.config_variables.get('loop_delay', 0.025))
                
            except Exception as e:
                self.update_status(f"Tracking error: {e}", "error")
                time.sleep(1)
                
        self.update_status("Tracking loop ended", "info")
        
    def _process_dual_hand_tracking(self, hmd_pose, left_pose, right_pose):
        """Process tracking data for both hands"""
        # Get HMD transformation
        m = hmd_pose.mDeviceToAbsoluteTracking
        hmd_position_world = self.get_position(m)
        hmd_matrix = [
            [m[0][0], m[0][1], m[0][2], m[0][3]],
            [m[1][0], m[1][1], m[1][2], m[1][3]],
            [m[2][0], m[2][1], m[2][2], m[2][3]]
        ]
        hmd_rotation_world = self.get_rotation(hmd_matrix)
        hmd_rotation_inverse = self.quaternion_conjugate(hmd_rotation_world)
        
        # Process right hand (primary weapon hand)
        r = right_pose.mDeviceToAbsoluteTracking
        right_position_world = self.get_position(r)
        right_matrix = [
            [r[0][0], r[0][1], r[0][2], r[0][3]],
            [r[1][0], r[1][1], r[1][2], r[1][3]],
            [r[2][0], r[2][1], r[2][2], r[2][3]]
        ]
        right_rotation_world = self.get_rotation(right_matrix)
        
        # Calculate right hand relative position
        right_diff_x = right_position_world.v[0] - hmd_position_world.v[0]
        right_diff_y = right_position_world.v[1] - hmd_position_world.v[1]
        right_diff_z = right_position_world.v[2] - hmd_position_world.v[2]
        right_diff_vector = openvr.HmdVector3_t()
        right_diff_vector.v = (ctypes.c_float * 3)(right_diff_x, right_diff_y, right_diff_z)
        
        right_relative_position = self.rotate_vector_by_quaternion(right_diff_vector, hmd_rotation_inverse)
        right_relative_rotation = self.quaternion_multiply(hmd_rotation_inverse, right_rotation_world)
        
        # Process left hand
        l = left_pose.mDeviceToAbsoluteTracking
        left_position_world = self.get_position(l)
        left_matrix = [
            [l[0][0], l[0][1], l[0][2], l[0][3]],
            [l[1][0], l[1][1], l[1][2], l[1][3]],
            [l[2][0], l[2][1], l[2][2], l[2][3]]
        ]
        left_rotation_world = self.get_rotation(left_matrix)
        
        # Calculate left hand relative position
        left_diff_x = left_position_world.v[0] - hmd_position_world.v[0]
        left_diff_y = left_position_world.v[1] - hmd_position_world.v[1]
        left_diff_z = left_position_world.v[2] - hmd_position_world.v[2]
        left_diff_vector = openvr.HmdVector3_t()
        left_diff_vector.v = (ctypes.c_float * 3)(left_diff_x, left_diff_y, left_diff_z)
        
        left_relative_position = self.rotate_vector_by_quaternion(left_diff_vector, hmd_rotation_inverse)
        left_relative_rotation = self.quaternion_multiply(hmd_rotation_inverse, left_rotation_world)
        
        # Check for two-handed weapon mode
        if self.config_variables.get('two_handed_weapon_mode', False):
            # Calculate distance between hands
            hand_distance = self.calculate_distance_xyz(
                right_relative_position.v[0], right_relative_position.v[1], right_relative_position.v[2],
                left_relative_position.v[0], left_relative_position.v[1], left_relative_position.v[2]
            )
            
            min_dist = self.config_variables.get('two_handed_min_distance', 0.2)
            max_dist = self.config_variables.get('two_handed_max_distance', 0.8)
            
            if min_dist <= hand_distance <= max_dist:
                # Two-handed grip detected - average the positions
                avg_x = (right_relative_position.v[0] + left_relative_position.v[0]) / 2
                avg_y = (right_relative_position.v[1] + left_relative_position.v[1]) / 2
                avg_z = (right_relative_position.v[2] + left_relative_position.v[2]) / 2
                
                # Use right hand rotation as primary
                self._update_tracking_from_relative(
                    avg_x, avg_y, avg_z,
                    right_relative_rotation,
                    hmd_rotation_world
                )
                return
        
        # Default: Use right hand for weapon
        self._update_tracking_from_relative(
            right_relative_position.v[0], right_relative_position.v[1], right_relative_position.v[2],
            right_relative_rotation,
            hmd_rotation_world
        )
        
    def _update_tracking_from_relative(self, rel_x, rel_y, rel_z, relative_rotation, hmd_rotation_world):
        """Update tracking data from relative position and rotation"""
        # InertiaController Bone Pose
        inertiaZ, inertiaX, inertiaY = rel_z, rel_x, rel_y
        inertiaZr, inertiaXr, inertiaYr = relative_rotation.x, relative_rotation.y, relative_rotation.z
        playerXr, playerZr, playerYr = hmd_rotation_world.x, hmd_rotation_world.y, hmd_rotation_world.z
        
        # Apply smoothing if enabled
        if self.smoother:
            inertiaX, inertiaY, inertiaZ = self.smoother.smooth_position(inertiaX, inertiaY, inertiaZ)
            smoothed_rot = self.smoother.smooth_rotation(
                relative_rotation.w, relative_rotation.x, 
                relative_rotation.y, relative_rotation.z
            )
            inertiaXr = smoothed_rot[1]
            inertiaYr = smoothed_rot[2]
            inertiaZr = smoothed_rot[3]
        
        # Store player rotation for gesture callbacks
        self.last_player_rotation = (playerXr, playerYr, playerZr)
        
        # Update tracking data
        self.update_tracking_data(inertiaX, inertiaY, inertiaZ, inertiaXr, inertiaYr, inertiaZr, inertiaZr, playerYr, -inertiaXr)
        
        # Update gesture recognition
        if self.gesture_recognizer:
            gesture_pos = (inertiaX, inertiaY, inertiaZ)
            self.gesture_recognizer.update(gesture_pos)