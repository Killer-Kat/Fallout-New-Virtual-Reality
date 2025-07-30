This is my attempt to translate and refine the changes that were made to the original FNVR tracker by m4rmzNexus who has improved the original by chaning from a rather slow (yet impressive) INI reading to storing it in memory instead. (I was gonna do that but why do something that has already been done) Sadly I don't speak Turkish, nor I assume do most people trying to mod Fallout NV. So if you found this hopefully it will help you. 

Original readme google translated:
This project aims to build upon the original Fallout: New Virtual Reality mod and elevate it to a level that offers a more stable, user-friendly, and "native" VR experience.
Purpose of the Project

The current mod offers an ingenious solution for adding VR motion controls to Fallout: New Vegas . However, it requires technical know-how and has some mechanical limitations. The goal of this project is to take this foundation and expand upon it using the following principles:

    User-Friendly: Installation and use of the mod should be simple and straightforward even for a non-technical player.
    Stability: The in-game experience should be smooth and error-free.
    Immersion: Mechanics should make the player feel like they are truly immersed in the game world.

Current Functionality

    Independent aiming with right hand controller
    Dual-handed support - Use left and right controllers simultaneously
    Two-handed weapon mode - Realistic two-handed wielding mechanics
    Advanced hand gesture recognition (dwell time, velocity tracking, cooldown)
    Easy control with graphical user interface (GUI)
    Ultra-low latency (<1ms) with memory-mapped file support
    Shake-free aiming with data smoothing (One Euro Filter)
    Dynamic controller detection
    Detailed error management and logging

Roadmap

The project will be developed in three main phases:
✅ Phase 1: Solidifying the Foundations and User Experience (UX)

    Configuration File: Managing settings (e.g. sensitivity, file path) from outside the code.
    Graphical Interface (GUI): A simple interface that will run the script with a single click.
    Error Management: Clear error messages and logging.

✅ Phase 2: Improving Core Mechanics

    IPC Boost: <1ms latency with memory-mapped files.
    Data Smoothing: Shake-free aiming with One Euro Filter.
    Advanced Motion Recognition: Reliable system with velocity tracking and dwell time.

✨ Phase 3: New Features and Depth

    Realistic Melee: Melee mechanics based on swing speed.
    Left Hand Support: For two-handed weapons and other interactions.
    Haptic Feedback: Vibration when shooting or taking damage.
    Physical Reload: Manual reload movements that increase immersion.

Setup
System Requirements

    Python >= 3.11
    SteamVR
    VR headsets and controllers (HTC Vive, Valve Index, Oculus, etc.)
    Fallout: New Vegas (Steam version)
    VorpX

Installation Steps
Install Python (3.11 or later)
Install dependencies:

pip install -r requirements.txt

config.iniconfigure file:

    ini_file_pathSet the value to your own Fallout New Vegas installation directory
    Example:E:/SteamLibrary/steamapps/common/Fallout New Vegas/Data/Config/Meh.ini
    If you want to use MMAP, mmap_file_pathalso set its value

Start SteamVR
Run the tracker:

python FNVR_Tracker.py

    In the GUI, follow these steps:
        Check the INI file path (change it with "Browse" if necessary)
        If desired, adjust the settings in the "Hand Selection" section:
            One-handed mode: Default, only the selected hand is tracked
            Two-handed mode: Both controllers are tracked
            Two-handed weapon mode: Can be used while two-handed mode is active
        Click the "Start" button
    Start the game with VorpX

Configuration (config.ini)

The mod now config.inireads all settings from its file. This file contains the following sections:

    [paths] : INI file path
    [position_scaling] : Position scaling and offset values
    [rotation_scaling] : Rotation scaling and offset values
    [pipboy_position] : Fixed position values for pipboy
    [pipboy_gesture] : Pipboy opening gesture settings
    [pause_menu_gesture] : Pause menu opening gesture settings
    [timing] : Timing settings (loop delay, key press times)
    [communication] : Communication method (mmap/ini) and MMAP file path
    [smoothing] : Data smoothing settings (filter type, strength)
    [gesture_recognition] : Advanced gesture recognition (dwell time, cooldown, velocity)
    [dual_hand] : Two-handed support settings

GUI Usage
Ana Controls

    Start/Stop : Starts or stops VR tracking
    INI File Path : Allows you to select the game's INI file

Hand Pick

    Enable Two-Handed Mode : Tracks both controllers
    Active Hand : Selects which hand to use in one-handed mode.
    Two-Handed Weapon Mode : Enables two-handed wielding mechanics (only in two-handed mode)

Smoothing Settings

    Enable Data Smoothing : Turns on/off the jitter reduction system
    Smoothing Strength : Adjusts how much smoothing is applied (0.1-5.0)

Status Indicators

    Status : General system status
    SteamVR : VR connection status
    Controller : Controller connection and tracking status
    Tracking : Active tracking status

Performance

When memory-mapped file (MMAP) mode is enabled:

    INI file writing : ~10-20ms
    MMAP write : <1ms
    Performance increase : 10-20x

Two-Handed Mode Features
One-Handed Mode (Default)

    Only the selected hand (right or left) is tracked
    The other hand is ignored
    Less processor usage

Two-Handed Mode

    Both controllers are detected and tracked
    Infrastructure for future two-handed interaction features
    Two-handed weapon mode can be activated

Two-Handed Weapon Mode

    The distance between two controllers is calculated
    When the hands are at a certain distance, the gun behaves as if it were held with two hands.
    Provides more stable aiming
    Min/max distance can be set from config

You can review the folder for detailed information and development plan docs.
Contribute

The project is open and we welcome your contributions. Please get involved by opening an issue or submitting a pull request.
