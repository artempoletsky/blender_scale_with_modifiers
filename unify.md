# Apply scale with modifiers

Used to unify visual size of modifiers. 

## Usage

In object mode select objects needed to be edited. Select the last object to make it active. 

Press ctrl + L. Select `Unify modifiers` option.

## How it works.

The script searches modifiers with same type from the bottom of the modifiers stack to top, and copies them.

![](https://raw.githubusercontent.com/artempoletsky/blender_scale_with_modifiers/master/img/example%202.png)

You can disallow the script to affect some modifiers by hiding them in viewport on the `active` object. 
In this case they will still affect the position of others modifiers.

For example, you have 2 objects with 2 bevels. 
And you want to copy the first bevel of the first object to the first bevel of the second object.

![](https://raw.githubusercontent.com/artempoletsky/blender_scale_with_modifiers/master/img/example%201.png)

You will get the same result, if you will press `Use names` option in this example. 

## Options

1. `Use names` - The script will match modifiers name instead of position.
Use it if you want the script working from the top of the stack to the bottom as well.
2. `Copy all attributes` - The script will copy all modifiers attributes, not only the size. 


## Supported modifiers and their properties

