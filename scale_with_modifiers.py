bl_info = {
    "name": "Scale with modifiers",
    "author": "Artem Poletsky",
    "version": (1, 4, 3),
    "blender": (2, 82, 0),
    "location": "Object > Apply > Apply scale with modifiers",
    "description": "Adds operator which applies scale to an object and its modifiers",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy
from mathutils import Vector

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
    'REMESH': {'voxel_size'},
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

def funcARRAYget(mod):
    return Vector((mod.constant_offset_displace[0], mod.constant_offset_displace[1], mod.constant_offset_displace[2], mod.merge_threshold))

def funcARRAYset(mod, size):
    mod.constant_offset_displace[0] = size[0]
    mod.constant_offset_displace[1] = size[1]
    mod.constant_offset_displace[2] = size[2]
    mod.merge_threshold = size[3]

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

def funcDISPLACEget(mod):
    return mod.strength

def funcDISPLACEset(mod, size):
    mod.strength = size

def funcSKIN(mod, scale, object, operator):
    verts = object.data.skin_vertices[0].data
    for v in verts:
        v.radius[0] *= scale
        v.radius[1] *= scale

def funcSKINget(mod):
    # unsupported
    return 1

def funcSKINset(mod, size):
    # unsupported
    return

def getModifierSize(mod, scale):
    attr = MODS[mod.type]
    if attr == 'function':
        return globals()["func" + mod.type + "get"](mod) * scale
    tupl = ()
    for key in attr:
        if not hasattr(mod, key):
            continue
        tupl += (getattr(mod, key), )
    if len(tupl) == 0:
        return 1
    if len(tupl) == 1:
        return tupl[0] * scale
    return Vector(tupl) * scale

def setModifierSize(mod, size):
    attr = MODS[mod.type]
    if attr == 'function':
        globals()["func" + mod.type + "set"](mod, size)
        return

    i = 0
    for key in attr:
        if not hasattr(mod, key):
            continue
        if type(size) == Vector:
            setattr(mod, key, size[i])
        else:
            setattr(mod, key, size)
        i+=1

def get_scale(obj):
    s = obj.scale
    return (s[0] + s[1] + s[2]) / 3

def equal_points_len(target, source):
    tl = len(target)
    sl = len(source)
    if tl == sl:
        return
    while tl > sl:
        target.remove(target[1])
        tl = len(target)
    while tl < sl:
        target.add(0, 0)
        tl = len(target)
    return
def copy_profile(target, source):
    copy_modifier(target, source)
    equal_points_len(target.points, source.points)
    # len = max(len(source.points), len(target.points))
    for i in range(0, len(source.points)):
        p1 = source.points[i]
        p2 = target.points[i]
        # new_point = target.points.add(p.location[0], p.location[1])
        p2.handle_type_1 = p1.handle_type_1
        p2.handle_type_2 = p1.handle_type_2
        p2.location = p1.location
        # copy_modifier(new_point, p)
    target.update()
    return

def copy_modifier(target, source, string=""):
    """Copy attributes from source to target that have string in them"""
    for attr in dir(source):
        if attr in {'custom_profile'}:
            copy_profile(getattr(target, attr), getattr(source, attr))
            continue
        if attr.find(string) > -1:
            try:
                setattr(target, attr, getattr(source, attr))
            except:
                pass
    return

class UnifyModifiersSizeOperator(bpy.types.Operator):
    """Unify modifiers"""
    bl_idname = "object.unify_modifiers_operator"
    bl_label = "Unify modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    use_names: bpy.props.BoolProperty(name="Use names", default=False)
    copy_all: bpy.props.BoolProperty(name="Copy all attributes", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.mode == 'OBJECT')

    def execute(self, context):
        source  = context.view_layer.objects.active
        targets = list(context.selected_objects)
        targets.remove(source)
        source_scale = get_scale(source)
        indices = {}
        for mod in reversed(source.modifiers):
            if not mod.type in MODS:
                continue
            size = getModifierSize(mod, source_scale)
            indices[mod.type] = indices[mod.type] + 1 if mod.type in indices else 0
            if not mod.show_viewport:
                continue
            source_index = indices[mod.type]
            for t in targets:
                target_scale = get_scale(t)
                target_index = 0
                for m in reversed(t.modifiers):
                    # print(source_index, target_index, mod.type, m.type)
                    if m.type == mod.type:
                        do_set_size = self.use_names and m.name == mod.name
                        # print(self.use_names, m.name, mod.name, do_set_size)
                        if not do_set_size and not self.use_names:
                            do_set_size = target_index == source_index
                        if do_set_size and target_scale != 0:
                            if self.copy_all:
                                copy_modifier(m, mod)
                            setModifierSize(m, size / target_scale)
                        target_index += 1
        return {'FINISHED'}


class ScaleWithModifiersOperator(bpy.types.Operator):
    """Apply scale with modifiers"""
    bl_idname = "object.scale_with_modifiers_operator"
    bl_label = "Apply scale with modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    deselect : bpy.props.BoolProperty(name="Deselect problem objects", default=False)
    scaleTextures: bpy.props.BoolProperty(name="Scale procedural displacement textures", default=False)
    makeClonesReal: bpy.props.BoolProperty(name="Make objects single user", default=False)

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

        warningMessage = "";

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
                    warningMessage = "Objects are single user now. "
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
                            if not hasattr(mod, attrname):
                                continue
                            val = getattr(mod, attrname)
                            setattr(mod, attrname, val * scale)



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


def menu_apply(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(ScaleWithModifiersOperator.bl_idname, text=ScaleWithModifiersOperator.bl_label)

def menu_make_links(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(UnifyModifiersSizeOperator.bl_idname, text=UnifyModifiersSizeOperator.bl_label)

classes = (
    ScaleWithModifiersOperator,
    UnifyModifiersSizeOperator,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


    bpy.types.VIEW3D_MT_object_apply.append(menu_apply)
    bpy.types.VIEW3D_MT_make_links.append(menu_make_links)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.types.VIEW3D_MT_object_apply.remove(menu_func)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_make_links)



if __name__ == "__main__":
    register()
