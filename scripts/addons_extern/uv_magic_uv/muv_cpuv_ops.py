# <pep8-80 compliant>

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bmesh
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty
from . import muv_common

__author__ = "Nutti <nutti.metro@gmail.com>"
__status__ = "production"
__version__ = "4.0"
__date__ = "XX XXX 2015"


# copy UV (sub menu operator)
class MUV_CPUVCopyUV(bpy.types.Operator):
    bl_idname = "uv.muv_cpuv_copy_uv"
    bl_label = "Copy UV Ops"
    bl_options = {'REGISTER', 'UNDO'}

    uv_map = bpy.props.StringProperty(options={'HIDDEN'})
    

    def execute(self, context):
        props = context.scene.muv_props.cpuv
        if self.uv_map == "":
            self.report({'INFO'}, "Copy UV coordinate.")
        else:
            self.report({'INFO'}, "Copy UV coordinate.(UV map:" + self.uv_map + ")")
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        if muv_common.check_version(2, 73, 0) >= 0:
            bm.faces.ensure_lookup_table()
        if self.uv_map == "":
            # get UV layer
            if not bm.loops.layers.uv:
                self.report({'WARNING'}, "Object must have more than one UV map.")
                return {'CANCELLED'}
            uv_layer = bm.loops.layers.uv.verify()
        else:
            uv_layer = bm.loops.layers.uv[self.uv_map]

        # get selected face
        props.src_uvs = []
        props.src_pin_uvs = []
        for face in bm.faces:
            if face.select:
                uvs = []
                pin_uvs = []
                for l in face.loops:
                    uvs.append(l[uv_layer].uv.copy())
                    pin_uvs.append(l[uv_layer].pin_uv)
                props.src_uvs.append(uvs)
                props.src_pin_uvs.append(pin_uvs)
        if len(props.src_uvs) == 0 or len(props.src_pin_uvs) == 0:
            self.report({'WARNING'}, "No faces are selected.")
            return {'CANCELLED'}
        self.report({'INFO'}, "%d face(s) are selected." % len(props.src_uvs))

        return {'FINISHED'}


# copy UV
class MUV_CPUVCopyUVMenu(bpy.types.Menu):
    """Copying UV coordinate on selected object."""

    bl_idname = "uv.muv_cpuv_copy_uv_menu"
    bl_label = "Copy UV"
    bl_description = "Copy UV"

    def draw(self, context):
        layout = self.layout
        # create sub menu
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        uv_maps = bm.loops.layers.uv.keys()
        layout.operator(
            MUV_CPUVCopyUV.bl_idname,
            text="[Default]", icon="PLUGIN").uv_map = ""
        for m in uv_maps:
            layout.operator(
                MUV_CPUVCopyUV.bl_idname,
                text=m, icon="PLUGIN").uv_map = m


# paste UV (sub menu operator)
class MUV_CPUVPasteUV(bpy.types.Operator):
    bl_idname = "uv.muv_cpuv_paste_uv"
    bl_label = "Paste UV Ops"
    bl_options = {'REGISTER', 'UNDO'}

    uv_map = bpy.props.StringProperty(options={'HIDDEN'})

    strategy = EnumProperty(
        name="Strategy",
        description="Paste Strategy",
        items=[
            ('N_N', 'N:N', 'Number of faces must be equal to source'),
            ('N_M', 'N:M', 'Number of faces must not be equal to source')],
        default="N_N")

    flip_copied_uv = BoolProperty(
        name="Flip Copied UV",
        description="Flip Copied UV...",
        default=False)

    rotate_copied_uv = IntProperty(
        default=0,
        name="Rotate Copied UV",
        min=0,
        max=30)

    def execute(self, context):
        props = context.scene.muv_props.cpuv
        if len(props.src_uvs) == 0 or len(props.src_pin_uvs) == 0:
            self.report({'WARNING'}, "Do copy operation at first.")
            return {'CANCELLED'}
        if self.uv_map == "":
            self.report({'INFO'}, "Paste UV coordinate.")
        else:
            self.report(
                {'INFO'}, "Paste UV coordinate. (UV map:" + self.uv_map + ")")
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        if muv_common.check_version(2, 73, 0) >= 0:
            bm.faces.ensure_lookup_table()
        if self.uv_map == "":
            # get UV layer
            if not bm.loops.layers.uv:
                self.report({'WARNING'}, "Object must have more than one UV map.")
                return {'CANCELLED'}
            uv_layer = bm.loops.layers.uv.verify()
        else:
            uv_layer = bm.loops.layers.uv[self.uv_map]
        
        # get selected face
        dest_uvs = []
        dest_pin_uvs = []
        dest_face_indices = []
        for face in bm.faces:
            if face.select:
                dest_face_indices.append(face.index)
                uvs = []
                pin_uvs = []
                for l in face.loops:
                    uvs.append(l[uv_layer].uv.copy())
                    pin_uvs.append(l[uv_layer].uv.copy())
                dest_uvs.append(uvs)
                dest_pin_uvs.append(pin_uvs)
        if len(dest_uvs) == 0 or len(dest_pin_uvs) == 0:
            self.report({'WARNING'}, "No faces are selected.")
            return {'CANCELLED'}
        if self.strategy == 'N_N' and len(props.src_uvs) != len(dest_uvs):
            self.report({'WARNING'}, "Number of selected faces is different from copied faces." +
                    "(src:%d, dest:%d)" %
                    (len(props.src_uvs), len(dest_uvs)))
            return {'CANCELLED'}
 
        # paste
        for i, idx in enumerate(dest_face_indices):
            suv = None
            spuv = None
            duv = None
            if self.strategy == 'N_N':
                suv = props.src_uvs[i]
                spuv = props.src_pin_uvs[i]
                duv = dest_uvs[i]
            elif self.strategy == 'N_M':
                suv = props.src_uvs[i % len(props.src_uvs)]
                spuv = props.src_pin_uvs[i % len(props.src_pin_uvs)]
                duv = dest_uvs[i]
            if len(suv) != len(duv):
                self.report({'WARNING'}, "Some faces are different size.")
                return {'CANCELLED'}
            suvs_fr = [uv.copy() for uv in suv]
            spuvs_fr = [pin_uv for pin_uv in spuv]
            # flip UVs
            if self.flip_copied_uv is True:
                suvs_fr.reverse()
                spuvs_fr.reverse()
            # rotate UVs
            for n in range(self.rotate_copied_uv):
                uv = suvs_fr.pop()
                pin_uv = spuvs_fr.pop()
                suvs_fr.insert(0, uv)
                spuvs_fr.insert(0, pin_uv)
            # paste UVs
            for l, suv, spuv in zip(bm.faces[idx].loops, suvs_fr, spuvs_fr):
                l[uv_layer].uv = suv
                l[uv_layer].pin_uv = spuv
        self.report({'INFO'}, "%d faces are copied." % len(dest_uvs))

        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}


# paste UV
class MUV_CPUVPasteUVMenu(bpy.types.Menu):
    """Copying UV coordinate on selected object."""

    bl_idname = "uv.muv_cpuv_paste_uv_menu"
    bl_label = "Paste UV"
    bl_description = "Paste UV"

    def draw(self, context):
        layout = self.layout
        # create sub menu
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        uv_maps = bm.loops.layers.uv.keys()
        layout.operator(
            MUV_CPUVPasteUV.bl_idname,
            text="[Default]", icon="PLUGIN").uv_map = ""
        for m in uv_maps:
            layout.operator(
                MUV_CPUVPasteUV.bl_idname,
                text=m, icon="PLUGIN").uv_map = m
