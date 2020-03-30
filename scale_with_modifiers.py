bl_info = {
    "name": "Scale with modifiers",
    "author": "Artem Poletsky",
    "version": (1, 2, 0),
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
    'DISPLACE':  'function',
    'SHRINKWRAP': {'offset'},
    'WELD': {'merge_threshold'},
    'SKIN': 'function',
}

def objectsSelectSet(objects, value):
    for o in objects:
        o.select_set(value)

def funcARRAY(mod, scale, object, operator):
    mod.constant_offset_displace[0] *= scale
    mod.constant_offset_displace[1] *= scale
    mod.constant_offset_displace[2] *= scale
    mod.merge_threshold *= scale
    return False

def funcDISPLACE(mod, scale, object, operator):
    mod.strength *= scale
    if (bool(mod.texture)
        & ((mod.texture_coords == "LOCAL") | (mod.texture_coords == "OBJECT"))
        & operator.scaleTextures):
        if hasattr(mod.texture, 'noise_scale'):
            mod.texture.noise_scale *= scale
        return "objects have displace texture applied."
    else:
        return False

def funcSKIN(mod, scale, object, operator):
    verts = object.data.skin_vertices[0].data
    for v in verts:
        v.radius[0] *= scale
        v.radius[1] *= scale

class ScaleWithModifiersOperator(bpy.types.Operator):
    """Apply scale with modifiers"""
    bl_idname = "object.scale_with_modifiers_operator"
    bl_label = "Apply scale with modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    deselect : bpy.props.BoolProperty(name="Deselect problem objects", default=False)
    scaleTextures: bpy.props.BoolProperty(name="Scale procedural displacement textures", default=True)
    makeClonesReal: bpy.props.BoolProperty(name="Make objects single user", default=True)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) > 0
            and context.object.mode == 'OBJECT')

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):

        objects = context.selected_objects

        notEven = []
        clones = []

        funcWarnings = [];
        
        isClonesModified = False

        for obj in objects:
            if not obj.data:
                continue

            users = obj.data.users
            if obj.data.use_fake_user:
                users-=1
            if users > 1:
                if self.makeClonesReal & (not isClonesModified):
                    isClonesModified = True
                    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)
                else:
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
                        result = globals()["func" + mod.type](mod, scale, obj, self)
                        if result:
                            funcWarnings.append((obj, result))
                    else:
                        for attrname in MODS[mod.type]:
                            val = getattr(mod, attrname)
                            setattr(mod, attrname, val * scale)

        warningMessage = "";

        warningObjects = []
        if len(funcWarnings):
            keys = {}
            for obj, w in funcWarnings:
                warningObjects.append(obj)

                if not w in keys:
                    keys[w] = 1
                else:
                    keys[w] += 1

            for k in keys:
                warningMessage += ("{:d} " + k + " ").format(keys[k])


        clonesLen = len(clones)
        if clonesLen:
            warningMessage += "{:d} objects are multi-user, ignoring ".format(clonesLen)
            objectsSelectSet(clones, False)

        notEvenLen = len(notEven)
        if notEvenLen:
            warningMessage += "Scale of {:d} objects is not even. ".format(notEvenLen)
        if warningMessage:
            self.report({'WARNING'}, warningMessage + "Some issues are possible ")
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)

        objectsSelectSet(clones, True)
        if self.deselect:
            objectsSelectSet(clones + notEven + warningObjects, False)

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
