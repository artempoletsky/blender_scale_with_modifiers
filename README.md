# Scale with modifiers 
Blender addon that's adds operator which applies scale to an object and its modifiers
## Download and installation

1. Download latest `scale_with_modifiers.py` from https://github.com/artempoletsky/blender_scale_with_modifiers/releases
2. In Blender's preferencies install addon from the file

## Usage

In object mode select objects needed to be edited. Press ctrl + A. Select `Apply scale with modifiers` option. 

For better results objects need to have even scale eg(0.5,0.5,0.5). For uneven objects warning will be displayed, and they will be deselected. 

Multy user objects will be ignored by the script and deselected. 

After script finish you can hide selected objects, and you will get only objects with possible issues.

You can disallow script to affect some modifiers by hiding them in the viewport.

## Supported modifiers and they properties

1. Array - Constant offset values
2. Screw - Screw offset
3. Solidify- Thickness
4. Wireframe - Thickness
5. Displace - Strength
6. Shrinkwwrap - Offset
