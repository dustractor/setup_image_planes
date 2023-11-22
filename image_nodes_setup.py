bl_info = {
    "name": "Setup Image Planes",
    "blender": (2,80,0),
    "version":(0,1),
    "category":"Image Planes" }


import bpy


class SETUP_img_plane_nodes(bpy.types.Operator):
    bl_idname = "setup.img_plane_nodes"
    bl_label = "setup image plane nodes"
    bl_options = {"REGISTER","UNDO"}
    def execute(self,context):
        print("self:",self)
        mats = list()
        for ob in bpy.data.objects:
            if ob.type == "MESH":
                mat = ob.data.materials[0]
                nt = mat.node_tree
                img_node = None
                for n in nt.nodes:
                    if n.type == "TEX_IMAGE":
                        img_node = n
                        break
                a_out = None
                for o in img_node.outputs:
                    if o.name == "Alpha":
                        a_out = o
                        break
                for l in a_out.links:
                    nt.links.remove(l)
                cd = None
                for n in nt.nodes:
                    if n.type == "CAMERA":
                        cd = n
                        break
                if not cd:
                    cd = nt.nodes.new("ShaderNodeCameraData")
                math_add = None
                for n in nt.nodes:
                    if n.type == "MATH" and n.operation == "ADD":
                        math_add = n
                        break
                if not math_add:
                    math_add = nt.nodes.new("ShaderNodeMath")
                    math_add.operation = "ADD"
                math_sub = None
                for n in nt.nodes:
                    if n.type == "MATH" and n.operation == "SUBTRACT":
                        math_sub = n
                        break
                if not math_sub:
                    math_sub = nt.nodes.new("ShaderNodeMath")
                    math_sub.operation = "SUBTRACT"
                    math_sub.use_clamp = True
                zdepth = None
                for o in cd.outputs:
                    if o.name == "View Z Depth":
                        zdepth = o
                math_add.inputs[1].default_value = 0.01
                add_input = math_add.inputs[0]
                add_output = math_add.outputs[0]
                math_sub.inputs[1].default_value = 1.0
                sub_input = math_sub.inputs[0]
                sub_output = math_sub.outputs[0]
                shader = None
                for n in nt.nodes:
                    if n.type == "BSDF_PRINCIPLED":
                        shader = n
                shader_in = None
                for i in shader.inputs:
                    if i.name == "Alpha":
                        shader_in = i
                nt.links.new(zdepth,add_input)
                nt.links.new(add_output,sub_input)
                nt.links.new(sub_output,shader_in)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(SETUP_img_plane_nodes)

def unregister():
    bpy.utils.unregister_class(SETUP_img_plane_nodes)

