"""
Memory-mapped file communication for ultra-low latency data transfer
between FNVR Tracker and Fallout New Vegas
"""

import mmap
import struct
import os
import logging
from typing import Tuple, Optional


class MMAPCommunicator:
    """Handle memory-mapped file communication for VR tracking data"""
    
    # Data structure format (all floats):
    # fCanIOpenThis, fiX, fiY, fiZ, fiXr, fiZr, fpZr
    # Total: 7 floats = 28 bytes
    STRUCT_FORMAT = '7f'
    STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)
    
    def __init__(self, mmap_path: str, logger: Optional[logging.Logger] = None):
        """
        Initialize MMAP communicator
        
        Args:
            mmap_path: Path to the memory-mapped file
            logger: Optional logger instance
        """
        self.mmap_path = mmap_path
        self.logger = logger or logging.getLogger(__name__)
        self.mmap_file = None
        self.file_handle = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize the memory-mapped file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.mmap_path), exist_ok=True)
            
            # Create or open the file
            if not os.path.exists(self.mmap_path):
                # Create file with initial size
                with open(self.mmap_path, 'wb') as f:
                    f.write(b'\x00' * self.STRUCT_SIZE)
                    
            # Open file for read/write
            self.file_handle = open(self.mmap_path, 'r+b')
            
            # Create memory map
            self.mmap_file = mmap.mmap(
                self.file_handle.fileno(),
                self.STRUCT_SIZE,
                access=mmap.ACCESS_WRITE
            )
            
            self.initialized = True
            self.logger.info(f"MMAP initialized at: {self.mmap_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MMAP: {e}")
            self.cleanup()
            return False
            
    def write_tracking_data(self, iX: float, iY: float, iZ: float, 
                          iXr: float, iYr: float, iZr: float, 
                          pXr: float, pYr: float, pZr: float,
                          config: dict) -> bool:
        """
        Write tracking data to memory-mapped file
        
        Args:
            iX, iY, iZ: Inertia position values
            iXr, iYr, iZr: Inertia rotation values
            pXr, pYr, pZr: Player rotation values
            config: Configuration dictionary with scaling values
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            # Calculate scaled values (same as INI format)
            scaled_values = (
                1.0,  # fCanIOpenThis
                (iX * config.get('x_scale', 50)) + config.get('x_offset', 15),
                (iY * config.get('y_scale', -50)) + config.get('y_offset', -10),
                (iZ * config.get('z_scale', -50)) + config.get('z_offset', 0),
                (iXr * config.get('xr_scale', -120)) + config.get('xr_offset', 10),
                (iZr * config.get('zr_scale', 120)) + config.get('zr_offset', -75),
                (pZr * config.get('pzr_scale', -150)) + config.get('pzr_offset', -7.5)
            )
            
            # Pack data into binary format
            packed_data = struct.pack(self.STRUCT_FORMAT, *scaled_values)
            
            # Write to memory-mapped file
            self.mmap_file.seek(0)
            self.mmap_file.write(packed_data)
            self.mmap_file.flush()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing to MMAP: {e}")
            return False
            
    def read_tracking_data(self) -> Optional[Tuple[float, ...]]:
        """
        Read tracking data from memory-mapped file
        
        Returns:
            Tuple of values or None if error
        """
        if not self.initialized:
            return None
            
        try:
            self.mmap_file.seek(0)
            packed_data = self.mmap_file.read(self.STRUCT_SIZE)
            values = struct.unpack(self.STRUCT_FORMAT, packed_data)
            return values
            
        except Exception as e:
            self.logger.error(f"Error reading from MMAP: {e}")
            return None
            
    def cleanup(self):
        """Clean up resources"""
        if self.mmap_file:
            try:
                self.mmap_file.close()
            except:
                pass
                
        if self.file_handle:
            try:
                self.file_handle.close()
            except:
                pass
                
        self.initialized = False
        
    def __enter__(self):
        """Context manager support"""
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.cleanup()
        
        
class MMAPBenchmark:
    """Benchmark utility to compare MMAP vs INI file performance"""
    
    @staticmethod
    def benchmark_write_speed(mmap_comm: MMAPCommunicator, 
                            ini_path: str, 
                            iterations: int = 1000) -> dict:
        """
        Benchmark write speed of MMAP vs INI file
        
        Returns:
            Dictionary with benchmark results
        """
        import time
        
        # Test data
        test_values = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
        test_config = {
            'x_scale': 50, 'x_offset': 15,
            'y_scale': -50, 'y_offset': -10,
            'z_scale': -50, 'z_offset': 0,
            'xr_scale': -120, 'xr_offset': 10,
            'zr_scale': 120, 'zr_offset': -75,
            'pzr_scale': -150, 'pzr_offset': -7.5
        }
        
        # Benchmark MMAP
        mmap_start = time.perf_counter()
        for _ in range(iterations):
            mmap_comm.write_tracking_data(*test_values, test_config)
        mmap_time = time.perf_counter() - mmap_start
        
        # Benchmark INI file
        ini_start = time.perf_counter()
        for _ in range(iterations):
            try:
                with open(ini_path, 'w') as f:
                    f.write("[Standard]\n")
                    f.write(f"fCanIOpenThis = 1\n")
                    f.write(f"fiX = {test_values[0]:.4f}\n")
                    f.write(f"fiY = {test_values[1]:.4f}\n")
                    f.write(f"fiZ = {test_values[2]:.4f}\n")
                    f.write(f"fiXr = {test_values[3]:.4f}\n")
                    f.write(f"fiZr = {test_values[4]:.4f}\n")
                    f.write(f"fpZr = {test_values[5]:.4f}\n")
            except:
                pass
        ini_time = time.perf_counter() - ini_start
        
        return {
            'iterations': iterations,
            'mmap_total_time': mmap_time,
            'mmap_avg_time_ms': (mmap_time / iterations) * 1000,
            'ini_total_time': ini_time,
            'ini_avg_time_ms': (ini_time / iterations) * 1000,
            'speedup_factor': ini_time / mmap_time
        }