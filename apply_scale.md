# Apply scale with modifiers

## Usage

In object mode select objects needed to be edited. Press ctrl + A. Select `Apply scale with modifiers` option.

For better results objects need to have even scale eg(0.5,0.5,0.5). 
For uneven objects warning will be displayed, and they will be deselected if the option is set.

You can disallow script to affect some modifiers by hiding them in the viewport.

## Options

1. Deselect problem objects. Useful to scale a large scene and find objects that can be broken. 
After script finish you can hide selected objects, and you will get only objects with possible issues.
2. Scale procedural textures. For procedural displace textures, depends on mapping type and texture type issues are possible. 
For more predictable results use UV mapping type. 
3. Make objects single user. Uses internal Blender operator of the same name before the opration. 
If False, multy user objects will be ignored by the script and deselected.

## Supported modifiers and their properties

1. Array - Constant offset values
2. Screw - Screw offset
3. Solidify- Thickness
4. Wireframe - Thickness
5. Displace - Strength, Scale of procedural textures for displace modifier
6. Shrinkwwrap - Offset
7. Skin - radius of vertices
8. Blender 2.83+ - Voxel remesh.
