# Scale with modifiers
Blender addon which adds operator which applies scale to an object and its modifiers. For Blender 2.8+

Demo: https://youtu.be/EdqKX0Vy6AM

## Download and installation

1. Download latest `scale_with_modifiers.py` from https://github.com/artempoletsky/blender_scale_with_modifiers/releases
2. In Blender's preferencies install addon from the file

## Usage

In object mode select objects needed to be edited. Press ctrl + A. Select `Apply scale with modifiers` option.

For better results objects need to have even scale eg(0.5,0.5,0.5). For uneven objects warning will be displayed, and they will be deselected.

Multy user objects will be ignored by the script and deselected.

For procedural displace textures, depends on mapping type and texture type issues are possible. For more predictable results use UV mapping type. 

After script finish you can hide selected objects, and you will get only objects with possible issues.

You can disallow script to affect some modifiers by hiding them in the viewport.

## Supported modifiers and they properties

1. Array - Constant offset values
2. Screw - Screw offset
3. Solidify- Thickness
4. Wireframe - Thickness
5. Displace - Strength, Scale of procedural textures for displace modifier
6. Shrinkwwrap - Offset
7. Skin - radius of vertices

You can support me on Gumroad, if you like my work. 
https://gum.co/MwiQk
