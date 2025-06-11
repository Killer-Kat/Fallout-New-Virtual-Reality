"""
Data smoothing algorithms for VR tracking data
Reduces jitter and provides stable aiming
"""

import numpy as np
from collections import deque
from typing import Tuple, Optional, Dict
import logging


class SmoothingFilter:
    """Base class for smoothing filters"""
    
    def __init__(self, window_size: int = 5):
        self.window_size = max(1, window_size)
        self.reset()
        
    def reset(self):
        """Reset filter state"""
        raise NotImplementedError
        
    def smooth(self, value: float) -> float:
        """Apply smoothing to a single value"""
        raise NotImplementedError
        

class MovingAverageFilter(SmoothingFilter):
    """Simple moving average filter"""
    
    def __init__(self, window_size: int = 5):
        super().__init__(window_size)
        
    def reset(self):
        """Reset filter state"""
        self.values = deque(maxlen=self.window_size)
        
    def smooth(self, value: float) -> float:
        """Apply moving average smoothing"""
        self.values.append(value)
        return sum(self.values) / len(self.values)
        

class ExponentialMovingAverageFilter(SmoothingFilter):
    """Exponential moving average filter - more responsive to recent changes"""
    
    def __init__(self, alpha: float = 0.3):
        """
        Args:
            alpha: Smoothing factor (0-1). Higher = less smoothing
        """
        self.alpha = max(0.0, min(1.0, alpha))
        self.reset()
        
    def reset(self):
        """Reset filter state"""
        self.ema = None
        
    def smooth(self, value: float) -> float:
        """Apply exponential moving average smoothing"""
        if self.ema is None:
            self.ema = value
        else:
            self.ema = self.alpha * value + (1 - self.alpha) * self.ema
        return self.ema
        

class OneEuroFilter(SmoothingFilter):
    """
    One Euro Filter - Adaptive filter that reduces jitter while preserving fast movements
    Based on: https://cristal.univ-lille.fr/~casiez/1euro/
    """
    
    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0):
        """
        Args:
            min_cutoff: Minimum cutoff frequency for position
            beta: Speed coefficient (higher = less lag during fast movements)
            d_cutoff: Cutoff frequency for derivative
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.reset()
        
    def reset(self):
        """Reset filter state"""
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None
        
    def smooth_with_time(self, value: float, timestamp: float) -> float:
        """Apply One Euro Filter with explicit timestamp"""
        if self.x_prev is None:
            self.x_prev = value
            self.t_prev = timestamp
            return value
            
        # Calculate time delta
        dt = timestamp - self.t_prev
        if dt <= 0:
            return self.x_prev
            
        # Calculate derivative
        dx = (value - self.x_prev) / dt
        
        # Filter derivative
        a_d = self._alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev
        
        # Calculate adaptive cutoff frequency
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        # Filter position
        a = self._alpha(cutoff, dt)
        x_hat = a * value + (1 - a) * self.x_prev
        
        # Update state
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = timestamp
        
        return x_hat
        
    def smooth(self, value: float) -> float:
        """Apply One Euro Filter using automatic timestamp"""
        import time
        return self.smooth_with_time(value, time.time())
        
    def _alpha(self, cutoff: float, dt: float) -> float:
        """Calculate smoothing factor alpha from cutoff frequency"""
        tau = 1.0 / (2.0 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)
        

class VectorSmoother:
    """Smooths 3D vectors (position/rotation)"""
    
    def __init__(self, filter_type: str = "moving_average", **filter_params):
        """
        Args:
            filter_type: Type of filter ("moving_average", "exponential", "one_euro")
            filter_params: Parameters for the specific filter
        """
        self.filter_type = filter_type
        self.filter_params = filter_params
        
        # Create filters for each axis
        self.filters = {
            'x': self._create_filter(),
            'y': self._create_filter(),
            'z': self._create_filter()
        }
        
    def _create_filter(self) -> SmoothingFilter:
        """Create a filter instance based on type"""
        if self.filter_type == "moving_average":
            return MovingAverageFilter(**self.filter_params)
        elif self.filter_type == "exponential":
            return ExponentialMovingAverageFilter(**self.filter_params)
        elif self.filter_type == "one_euro":
            return OneEuroFilter(**self.filter_params)
        else:
            raise ValueError(f"Unknown filter type: {self.filter_type}")
            
    def smooth(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Smooth a 3D vector"""
        return (
            self.filters['x'].smooth(x),
            self.filters['y'].smooth(y),
            self.filters['z'].smooth(z)
        )
        
    def reset(self):
        """Reset all filters"""
        for filter in self.filters.values():
            filter.reset()
            

class QuaternionSmoother:
    """Special smoother for quaternion rotations using SLERP"""
    
    def __init__(self, alpha: float = 0.3):
        """
        Args:
            alpha: Interpolation factor (0-1). Higher = less smoothing
        """
        self.alpha = max(0.0, min(1.0, alpha))
        self.prev_quat = None
        
    def smooth(self, w: float, x: float, y: float, z: float) -> Tuple[float, float, float, float]:
        """Smooth quaternion using SLERP (Spherical Linear Interpolation)"""
        # Normalize input quaternion
        norm = np.sqrt(w*w + x*x + y*y + z*z)
        if norm == 0:
            return (1, 0, 0, 0)
            
        q2 = np.array([w, x, y, z]) / norm
        
        if self.prev_quat is None:
            self.prev_quat = q2
            return tuple(q2)
            
        # Calculate dot product
        dot = np.dot(self.prev_quat, q2)
        
        # If quaternions are nearly opposite, use linear interpolation
        if dot < 0:
            q2 = -q2
            dot = -dot
            
        # If quaternions are very close, use linear interpolation
        if dot > 0.9995:
            result = self.prev_quat + self.alpha * (q2 - self.prev_quat)
            result = result / np.linalg.norm(result)
        else:
            # Use SLERP
            theta = np.arccos(dot)
            sin_theta = np.sin(theta)
            
            w1 = np.sin((1 - self.alpha) * theta) / sin_theta
            w2 = np.sin(self.alpha * theta) / sin_theta
            
            result = w1 * self.prev_quat + w2 * q2
            
        self.prev_quat = result
        return tuple(result)
        
    def reset(self):
        """Reset smoother state"""
        self.prev_quat = None
        

class TrackingSmoother:
    """Complete smoothing solution for VR tracking data"""
    
    def __init__(self, config: Dict, logger: Optional[logging.Logger] = None):
        """
        Initialize tracking smoother with configuration
        
        Args:
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Check if smoothing is enabled
        self.enabled = config.get('smoothing_enabled', True)
        if not self.enabled:
            self.logger.info("Smoothing disabled")
            return
            
        # Get filter settings
        filter_type = config.get('smoothing_filter', 'one_euro')
        
        # Position smoother
        if filter_type == 'one_euro':
            pos_params = {
                'min_cutoff': config.get('position_min_cutoff', 1.0),
                'beta': config.get('position_beta', 0.007)
            }
        elif filter_type == 'exponential':
            pos_params = {'alpha': config.get('position_alpha', 0.3)}
        else:  # moving_average
            pos_params = {'window_size': config.get('position_window_size', 5)}
            
        self.position_smoother = VectorSmoother(filter_type, **pos_params)
        
        # Rotation smoother (quaternion)
        self.rotation_smoother = QuaternionSmoother(
            alpha=config.get('rotation_alpha', 0.5)
        )
        
        self.logger.info(f"Smoothing initialized with {filter_type} filter")
        
    def smooth_position(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Smooth position data"""
        if not self.enabled:
            return (x, y, z)
        return self.position_smoother.smooth(x, y, z)
        
    def smooth_quaternion(self, w: float, x: float, y: float, z: float) -> Tuple[float, float, float, float]:
        """Smooth rotation quaternion"""
        if not self.enabled:
            return (w, x, y, z)
        return self.rotation_smoother.smooth(w, x, y, z)
        
    def reset(self):
        """Reset all smoothers"""
        if self.enabled:
            self.position_smoother.reset()
            self.rotation_smoother.reset()