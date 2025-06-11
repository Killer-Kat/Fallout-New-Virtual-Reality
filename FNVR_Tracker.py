#!/usr/bin/env python3
"""
Fallout: New Virtual Reality Tracker
Main entry point - launches GUI by default
For CLI mode, use: python FNVR_Tracker.py --cli
"""

import sys
import argparse
from app_gui import FNVRTrackerGUI
from tracker_logic import TrackerLogic


def run_cli_mode():
    """Run tracker in CLI mode (legacy behavior)"""
    print("Starting FNVR Tracker in CLI mode...")
    tracker = TrackerLogic()
    
    # Initialize VR
    if not tracker.init_vr():
        print("Failed to initialize VR. Make sure SteamVR is running.")
        return 1
        
    try:
        # Run tracking loop directly (blocking)
        tracker.running = True
        tracker._tracking_loop()
    except KeyboardInterrupt:
        print("\nStopping tracker...")
    finally:
        tracker.running = False
        tracker.shutdown_vr()
        
    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Fallout: New Virtual Reality Tracker")
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Run in CLI mode without GUI"
    )
    
    args = parser.parse_args()
    
    if args.cli:
        # Run in CLI mode
        return run_cli_mode()
    else:
        # Run with GUI (default)
        app = FNVRTrackerGUI()
        app.run()
        return 0


if __name__ == "__main__":
    sys.exit(main())