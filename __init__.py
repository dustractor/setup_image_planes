bl_info = {
    "name": "Setup Image Planes",
    "blender": (2,80,0),
    "category":"Image Planes"}


import bpy

def _(c=None,r=[]):
    if c:
        r.append(c)
        return c
    return r

def get_image_node(tree):
    for node in tree.nodes:
        if node.type == "TEX_IMAGE":
            return node

def get_camera_node(tree):
    n = None
    for node in tree.nodes:
        if node.type == "CAMERA":
            n = node
            break
    if not n:
        n = tree.nodes.new("ShaderNodeCameraData")
    return n

def get_add_node(tree):
    n = None
    for node in tree.nodes:
        if node.type == "MATH" and node.operation == "ADD":
            n = node
            break
    if not n:
        n = tree.nodes.new("ShaderNodeMath")
        n.operation = "ADD"
    return n

def get_subtract_node(tree):
    n = None
    for node in tree.nodes:
        if node.type == "MATH" and node.operation == "SUBTRACT":
            n = node
            break
    if not n:
        n = tree.nodes.new("ShaderNodeMath")
        n.operation = "SUBTRACT"
        n.use_clamp = True
    return n

def get_principled_shader_node(tree):
    for node in tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node

def get_input_by_name(node,name):
    for socket in node.inputs:
        if socket.name == name:
            return socket

def get_output_by_name(node,name):
    for socket in node.outputs:
        if socket.name == name:
            return socket

def unlink_output(tree,node):
    for link in node.links:
        tree.links.remove(link)

meshes = lambda _:_.type == "MESH"

@_
class SETUP_OT_img_plane_nodes(bpy.types.Operator):
    bl_idname = "setup.img_plane_nodes"
    bl_label = "setup image plane nodes"
    bl_options = {"REGISTER","UNDO"}
    def execute(self,context):
        cam = context.scene.camera
        cam.location = [0,0,2.8]
        cam.rotation_euler = [0,0,0]
        cam.data.lens = 76.0
        print("_"*40)
        z = 0
        for ob in filter(meshes,context.selected_objects):
            ob.location = [0,0,z]
            z -= 1
            ob.rotation_euler = [0,0,0]
            mat = ob.data.materials[0]
            tree = mat.node_tree
            image_node = get_image_node(tree)
            image_alpha_out = get_output_by_name(image_node,"Alpha")
            camera_node = get_camera_node(tree)
            add_node = get_add_node(tree)
            sub_node = get_subtract_node(tree)
            zdepth = get_output_by_name(camera_node,"View Z Depth")
            shader = get_principled_shader_node(tree)
            shader_alpha_in = get_input_by_name(shader,"Alpha")
            add_input = add_node.inputs[0]
            add_output = add_node.outputs[0]
            sub_input = sub_node.inputs[0]
            sub_output = sub_node.outputs[0]

            add_node.inputs[1].default_value = 0.01
            sub_node.inputs[1].default_value = 1.0

            unlink_output(tree,image_alpha_out)
            tree.links.new(zdepth,add_input)
            tree.links.new(add_output,sub_input)
            tree.links.new(sub_output,shader_alpha_in)

        return {"FINISHED"}

@_
class SETUP_PT_imageplanes(bpy.types.Panel):
    bl_label = "Setup Image Planes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ImagePlanes"
    def draw(self,context):
        layout = self.layout
        layout.operator("setup.img_plane_nodes")



menu_draw = lambda s,c:s.layout.operator("setup.img_plane_nodes")

def register():
    list(map(bpy.utils.register_class,_()))
    bpy.types.VIEW3D_MT_object.append(menu_draw)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_draw)
    list(map(bpy.utils.unregister_class,_()))

