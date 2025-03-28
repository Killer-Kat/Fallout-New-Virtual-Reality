Requirements:
Python >= 3.12 (Can probably get away with previous versions.)
Libraries: Keyboard, Openvr, and NumPy

Please change the file path string to your New Vegas /Data/Config/ path.
It won't work if you don't.

Run this program before entering New Vegas

DISCLAIMER:
This needs the 3rd party program VorpX to run as it renders the game in virtual reality.
You also need to run my python program, FNVR_Tracker, to grab headset and controller poses.
VorpX Link: https://www.vorpx.com (VorpX costs ~$40)
FNVR_Tracker Link: https://www.github.com/iloveusername/Fallout-New-Virtual-Reality
Vimeo Link:  https://vimeo.com/1070196230

What does this mod do?
﻿Fallout: New Virtual Reality brings virtual reality motion controls into Fallout: New Vegas. With vanilla VorpX and NV, your gun is strapped to your face and you shoot directly where you look. Using this mod, your weapon will follow your hand and shoot in the direction you're pointing it. You can also point your gun to select NPCs and containers, as well as pick up and move objects. You can also use gestures to open the Pip-Boy and ESC Menu. Movement is controller centric rather than HMD centric. Overall, it makes for a more engaging and entertaining New Vegas VR experience.

What quirks does it have?
Slows down when a lot of aggressive NPCs are attacking you.

Works great with pistols, but some two handed weapons will fire off-center.

Aiming down sights can be screwy. I recommend hip firing, it’s easier.

Only the right hand is used for VR motion control.

Melee is still just pressing a trigger rather than swinging.

With VorpX, use the recenter function if things feel off. Hold both grips to open the VorpX menu.

Bullets fire along the plane you are looking. This is to say, bullets end up vertically where you are looking but horizontally where you are pointing the gun. Basically, you can sweep your gun side to side just fine.

Is it perfect? Definitely not. Is it fun? Hell yeah.

How does it work?
This mod works by using a program I created to grab the XYZ coordinates and rotations of a VR headset and a VR controller. The program saves these values to an ini file, which is read by a script running every tick. Said script passes these variables to another script that updates the player’s pose every tick. There’s more going on of course, but you can check the source code to see what’s up if you really wanna know more. The fact that this works at all is wild.

How do I install and use it?
Download and install VorpX.
Download and install Python 3.12 if you don’t have it. I like to use Pycharm as my IDE.
Pip install the following libraries:
Keyboard
Openvr
Numpy
In the FNVR_Tracker.py file, please edit the file path to your FNV’s /Data/Config/ folder.
Make sure SteamVR is open.
Run the FNVR_Tracker.py program.
Download and install this mod using your mod manager of choice. Or manually by dragging and dropping into your Data folder.
Open VorpX, make sure it’s running.
Open Fallout: New Vegas through NVSE.
﻿VorpX should attach and if the FNVR_Tracker.py program is running, the mod should work.

Recommended VorpX settings:
First time loading in, you need get out of the bed in Doc Mitchell's house and hold the left grip down and then the right grip as well. This opens the VorpX menu. Click on full ﻿scan and let it do its thing. Click okay and save, then exit the game. Load back in and things should be okay.
Other than that, I recommend default settings except for setting controller visualization to off. Use it to learn hotkeys and whatnot but once you know what’s up you should keep it off.

More info:
This is actually my first mod, ever! Not only for New Vegas, but any game. I was watching a Youtube video about New Vegas in VorpX and saw how lacking it was, then the general idea and roadmap of this mod popped into my head and I got to work. I also saw a bunch of reddit posts saying that this would be a significantly difficult task or maybe even impossible, so I knew I had to give it a shot. This mod took around one week of free time grind to get to a fun and playable state, time well spent. To open your Pip boy, move your right hand upwards from a resting hip fire position. To open the pause menu, move your right hand a bit over your heart.

How compatible is it with other mods?
﻿I believe this mod is compatible with all different kinds of mods. This mod messes with the poses and rotations of the 1st person player skeleton, so anything that doesn’t mess with that should be fine. I’m really excited to see what kinds of mods you guys find that work really well with motion controls in VR. I’m also uploading the code to Github so people can work on it themselves and try to take things further than me.

Required Mods:
NVSE
JIP LN NVSE Plugin
JohnnyGuitar NVSE
NV 4GB Extender Patch

Recommended Mods (So Far):
Any bullet time mod. (Feels cool)
Lead Bullet Ballistics (Lets you see where your bullets are actually going + also feels cool).
Bug fix mods.

Credit:
I would like to acknowledge the B42 Weapon Inertia mod by Xilandro for helping me understand the basics of how to move the character’s first person pose.
I would also like to credit the NV Compatibility Skeleton mod and its many creators for being the base skeleton that I modify.

Usage:
Use this code and mod as you see fit, but please keep it open source. Give credit too.
