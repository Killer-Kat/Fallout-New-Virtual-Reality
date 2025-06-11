"""
Advanced gesture recognition system for VR controllers
Prevents accidental triggers and provides reliable gesture detection
"""

import time
import numpy as np
from collections import deque
from typing import Tuple, Optional, Dict, Callable
import logging


class GestureZone:
    """Represents a 3D zone for gesture detection"""
    
    def __init__(self, center: Tuple[float, float, float], radius: float, gesture_id: str):
        """
        Args:
            center: (x, y, z) center point of the gesture zone
            radius: Detection radius
            gesture_id: Unique identifier for this gesture
        """
        self.center = np.array(center)
        self.radius = radius
        self.gesture_id = gesture_id
        self.entry_time = None
        self.is_inside = False
        self.last_trigger_time = 0
        
    def check_position(self, pos: Tuple[float, float, float]) -> bool:
        """Check if position is inside the gesture zone"""
        position = np.array(pos)
        distance = np.linalg.norm(position - self.center)
        return distance < self.radius
        

class VelocityTracker:
    """Tracks velocity of controller movement"""
    
    def __init__(self, window_size: int = 10):
        """
        Args:
            window_size: Number of samples to use for velocity calculation
        """
        self.positions = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        
    def update(self, position: Tuple[float, float, float], timestamp: float = None):
        """Update with new position"""
        if timestamp is None:
            timestamp = time.time()
            
        self.positions.append(np.array(position))
        self.timestamps.append(timestamp)
        
    def get_velocity(self) -> float:
        """Calculate current velocity magnitude"""
        if len(self.positions) < 2:
            return 0.0
            
        # Calculate average velocity over the window
        velocities = []
        for i in range(1, len(self.positions)):
            dt = self.timestamps[i] - self.timestamps[i-1]
            if dt > 0:
                dp = self.positions[i] - self.positions[i-1]
                velocity = np.linalg.norm(dp) / dt
                velocities.append(velocity)
                
        return np.mean(velocities) if velocities else 0.0
        
    def get_direction(self) -> Optional[np.ndarray]:
        """Get average movement direction"""
        if len(self.positions) < 2:
            return None
            
        # Calculate average direction
        directions = []
        for i in range(1, len(self.positions)):
            dp = self.positions[i] - self.positions[i-1]
            norm = np.linalg.norm(dp)
            if norm > 0:
                directions.append(dp / norm)
                
        if directions:
            avg_direction = np.mean(directions, axis=0)
            norm = np.linalg.norm(avg_direction)
            if norm > 0:
                return avg_direction / norm
                
        return None
        
    def reset(self):
        """Reset velocity tracking"""
        self.positions.clear()
        self.timestamps.clear()
        

class GestureRecognizer:
    """Advanced gesture recognition with velocity and dwell time"""
    
    def __init__(self, config: Dict, logger: Optional[logging.Logger] = None):
        """
        Initialize gesture recognizer
        
        Args:
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Gesture parameters
        self.dwell_time = config.get('gesture_dwell_time', 0.5)
        self.cooldown_time = config.get('gesture_cooldown', 1.0)
        self.max_velocity = config.get('gesture_max_velocity', 0.5)
        self.enabled = config.get('gesture_recognition_enabled', True)
        
        # Create gesture zones
        self.gesture_zones = {}
        self._create_gesture_zones()
        
        # Velocity tracker
        self.velocity_tracker = VelocityTracker()
        
        # Gesture callbacks
        self.gesture_callbacks = {}
        
        self.logger.info("Advanced gesture recognition initialized")
        
    def _create_gesture_zones(self):
        """Create gesture detection zones from config"""
        # Pipboy gesture
        self.gesture_zones['pipboy'] = GestureZone(
            center=(
                self.config.get('gesture_x', 0.12),
                self.config.get('gesture_y', 0.24),
                self.config.get('gesture_z', -0.29)
            ),
            radius=self.config.get('gesture_threshold', 0.1),
            gesture_id='pipboy'
        )
        
        # Pause menu gesture
        self.gesture_zones['pause'] = GestureZone(
            center=(
                self.config.get('pause_x', -0.3158),
                self.config.get('pause_y', -0.1897),
                self.config.get('pause_z', -0.1316)
            ),
            radius=self.config.get('pause_threshold', 0.1),
            gesture_id='pause'
        )
        
    def register_gesture_callback(self, gesture_id: str, callback: Callable):
        """Register a callback for when a gesture is recognized"""
        self.gesture_callbacks[gesture_id] = callback
        
    def update(self, position: Tuple[float, float, float], timestamp: float = None) -> Optional[str]:
        """
        Update gesture recognition with new position
        
        Args:
            position: Current controller position
            timestamp: Optional timestamp
            
        Returns:
            Gesture ID if a gesture was triggered, None otherwise
        """
        if not self.enabled:
            return None
            
        if timestamp is None:
            timestamp = time.time()
            
        # Update velocity tracking
        self.velocity_tracker.update(position, timestamp)
        velocity = self.velocity_tracker.get_velocity()
        
        triggered_gesture = None
        
        # Check each gesture zone
        for zone_id, zone in self.gesture_zones.items():
            is_inside = zone.check_position(position)
            
            if is_inside and not zone.is_inside:
                # Just entered the zone
                zone.is_inside = True
                zone.entry_time = timestamp
                self.logger.debug(f"Entered {zone_id} gesture zone")
                
            elif not is_inside and zone.is_inside:
                # Just left the zone
                zone.is_inside = False
                zone.entry_time = None
                self.logger.debug(f"Left {zone_id} gesture zone")
                
            elif is_inside and zone.is_inside:
                # Still inside the zone
                if zone.entry_time is not None:
                    # Check dwell time
                    dwell_duration = timestamp - zone.entry_time
                    
                    if dwell_duration >= self.dwell_time:
                        # Check velocity (must be relatively still)
                        if velocity <= self.max_velocity:
                            # Check cooldown
                            time_since_last = timestamp - zone.last_trigger_time
                            
                            if time_since_last >= self.cooldown_time:
                                # Trigger gesture!
                                zone.last_trigger_time = timestamp
                                zone.entry_time = None  # Reset to prevent re-triggering
                                triggered_gesture = zone_id
                                
                                self.logger.info(f"Gesture triggered: {zone_id}")
                                
                                # Call registered callback
                                if zone_id in self.gesture_callbacks:
                                    self.gesture_callbacks[zone_id]()
                                    
                        else:
                            # Moving too fast, reset entry time
                            zone.entry_time = timestamp
                            
        return triggered_gesture
        
    def get_zone_status(self, zone_id: str) -> Dict:
        """Get current status of a gesture zone"""
        if zone_id not in self.gesture_zones:
            return {}
            
        zone = self.gesture_zones[zone_id]
        now = time.time()
        
        status = {
            'is_inside': zone.is_inside,
            'progress': 0.0,
            'can_trigger': True
        }
        
        if zone.is_inside and zone.entry_time is not None:
            dwell_duration = now - zone.entry_time
            status['progress'] = min(1.0, dwell_duration / self.dwell_time)
            
        # Check cooldown
        time_since_last = now - zone.last_trigger_time
        if time_since_last < self.cooldown_time:
            status['can_trigger'] = False
            status['cooldown_remaining'] = self.cooldown_time - time_since_last
            
        return status
        
    def reset(self):
        """Reset all gesture states"""
        for zone in self.gesture_zones.values():
            zone.is_inside = False
            zone.entry_time = None
            
        self.velocity_tracker.reset()
        

class GestureVisualizer:
    """Helper class for visualizing gesture states in GUI"""
    
    @staticmethod
    def get_progress_bar(progress: float, width: int = 20) -> str:
        """Create ASCII progress bar"""
        filled = int(progress * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {int(progress * 100)}%"
        
    @staticmethod
    def get_status_text(status: Dict) -> str:
        """Convert gesture status to readable text"""
        if not status.get('is_inside', False):
            return "Dışarıda"
            
        if not status.get('can_trigger', True):
            cooldown = status.get('cooldown_remaining', 0)
            return f"Bekleme: {cooldown:.1f}s"
            
        progress = status.get('progress', 0)
        if progress < 1.0:
            return f"Dolduruluyor: {int(progress * 100)}%"
        else:
            return "Hazır!"