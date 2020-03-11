bl_info = {
    "name": "Scale with modifiers",
    "author": "Artem Poletsky",
    "version": (1, 0, 1),
    "blender": (2, 82, 0),
    "location": "Object > Apply > Apply scale with modifiers",
    "description": "Adds operator which applies scale to an object and its modifiers",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy

MODS = {
    'ARRAY': 'function',
    'BOOLEAN': {'double_threshold'},
    'BEVEL': {'width'},
    'SCREW': {'screw_offset', 'merge_threshold'},
    'MIRROR': {'merge_threshold'},
    'SOLIDIFY': {'thickness'},
    'WIREFRAME': {'thickness'},
    'DISPLACE': {'strength'},
    'SHRINKWRAP': {'offset'},
    'WELD': {'merge_threshold'},
}

def funcARRAY(mod, scale):
    mod.constant_offset_displace[0] *= scale
    mod.constant_offset_displace[1] *= scale
    mod.constant_offset_displace[2] *= scale
    mod.merge_threshold *= scale
    

class ScaleWithModifiersOperator(bpy.types.Operator):
    """Apply scale with modifiers"""
    bl_idname = "object.scale_with_modifiers_operator"
    bl_label = "Apply scale with modifiers"

#    @classmethod
#    def poll(cls, context):
#        return len(context.selected_objects) == 2

    def execute(self, context):
        
        notEven = []
        clones = []
        
        for obj in context.selected_objects:
            if not obj.data:
                continue
            
            users = obj.data.users
            if obj.data.use_fake_user:
                users-=1
            if users > 1:
                clones.append(obj)
                continue
            
            s = obj.scale
            isEven = s[0] == s[1] == s[2]
            if not isEven:
                notEven.append(obj)
                
            
            scale = (s[0] + s[1] + s[2]) / 3
             
            for mod in obj.modifiers:
                
                if (mod.type in MODS) & mod.show_viewport:
                    if MODS[mod.type] == 'function':
                        globals()["func" + mod.type](mod, scale)
                    else:    
                        for attrname in MODS[mod.type]:
                            val = getattr(mod, attrname)
                            setattr(mod, attrname, val * scale)
        
        warningMessage = "";
        clonesLen = len(clones)
        if clonesLen:
             warningMessage += "{:d} objects are multi-user, ignoring ".format(clonesLen)
             for o in clones:
                 o.select_set(False)
                 
        notEvenLen = len(notEven)
        if notEvenLen:
            warningMessage += "Scale of {:d} objects is not even. Some issues are possible ".format(notEvenLen)
        if warningMessage:
            self.report({'WARNING'}, warningMessage)
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
        for o in notEven:
                 o.select_set(False)
        return { 'FINISHED' }
    

def menu_func(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(ScaleWithModifiersOperator.bl_idname, text=ScaleWithModifiersOperator.bl_label)


classes = (
    ScaleWithModifiersOperator,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    bpy.types.VIEW3D_MT_object_apply.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.types.VIEW3D_MT_object_apply.remove(menu_func)

    

if __name__ == "__main__":
    register()
