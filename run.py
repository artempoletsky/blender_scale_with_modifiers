import sys
import os
import bpy

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import scale_with_modifiers
import imp
imp.reload(scale_with_modifiers)
scale_with_modifiers.register()
