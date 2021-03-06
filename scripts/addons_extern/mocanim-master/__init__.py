#====================== BEGIN GPL LICENSE BLOCK ======================
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
#======================= END GPL LICENSE BLOCK ========================

bl_info = {
    "name": "MocAnim",
    "version": (0, 1),
    "author": "Lucio Rossi",
    "blender": (2, 74, 0),
    "description": "Motion Capture Rig Animation",
    "location": "View3D > Tools > MocAnim",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"}

if "bpy" in locals():
    import imp
    imp.reload(ui)
    imp.reload(bind_animation)
    imp.reload(keyframing)
    imp.reload(fkik)
    imp.reload(utils)

else:
    import bpy
    from . import ui
    from . import bind_animation
    from . import fkik
    from . import utils
    from . import keyframing
    
    from bpy.props import (BoolProperty,
                       CollectionProperty,
                       EnumProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       IntProperty,
                       PointerProperty,
                       StringProperty,
                       )
import os

######## REGISTER ########

def update_export_path(self, context):
        scn = context.scene
        pathname, filename = os.path.split(scn.MocanimExportPath)
        if 'bvh' not in filename.split('.'):
            filename = '.'.join(filename.split('.')[0:-1]) + '.bvh'
        else: return

        scn.MocanimExportPath = bpy.path.abspath(os.path.join(pathname, filename))

def register():

    ui.register()
    bind_animation.register()
    keyframing.register()
    fkik.register()

    bpy.types.Scene.MocanimExportPath = bpy.props.StringProperty(name='Mocanim Export Path',default='//./',description='Path to Export Mocanimator', subtype='FILE_PATH', update=update_export_path)

    bpy.types.Scene.MocanimSrcRig = bpy.props.StringProperty(name='Metarig Rig',default='metarig',description='Meta-Rig for Mocanim plugin')
    bpy.types.Scene.MocanimTrgRig = bpy.props.StringProperty(name='Character Rig',default='rig',description='Character Rig for Mocanim plugin')
    bpy.types.Scene.MocanimFkIkArms = BoolProperty(name='Transfer Arms', description='transfer kinematics on Arms', default=True)
    bpy.types.Scene.MocanimFkIkLegs = BoolProperty(name='Transfer Legs', description='transfer kinematics on Legs', default=True)
    
    bpy.types.Scene.MocanimArmsIk = BoolProperty(name='IK Arms', description='transfer kinematics on Arms', default=True)
    bpy.types.Scene.MocanimLegsIk = BoolProperty(name='IK Legs', description='transfer kinematics on Legs', default=True)

    bpy.types.Scene.MocanimAdvOptions = BoolProperty(name="Advanced Options",description="Enable Advanced Options",default=False)
    bpy.types.Scene.MocanimConstrainRoot = BoolProperty(name="Constrain Root",description="Constrain the root bone",default=True)
    bpy.types.Scene.MocanimConstrainSpine = BoolProperty(name="Constrain Spine",description="Constrain spine bones",default=True)
    bpy.types.Scene.MocanimConstrainArms = BoolProperty(name="Constrain Arms",description="Constrain arm bones",default=True)
    bpy.types.Scene.MocanimConstrainLegs = BoolProperty(name="Constrain Legs",description="Constrain leg bones",default=True)
    bpy.types.Scene.MocanimConstrainTorso = BoolProperty(name="Constrain Torso",description="Constrain torso bone",default=True)
    bpy.types.Scene.MocanimConstrainHips = BoolProperty(name="Constrain Hips",description="Constrain hip bones",default=True)
    bpy.types.Scene.MocanimConstrainChest = BoolProperty(name="Constrain Chest",description="Constrain chest bone",default=True)
    bpy.types.Scene.MocanimFollowThigh = BoolProperty(name="Follow thighs",description="Hips follow thigh bones",default=True)
    bpy.types.Scene.MocanimUseLimits = BoolProperty(name="Use Limits",description="Use Bone Limits",default=True)

def unregister():

    ui.unregister()
    bind_animation.unregister()
    keyframing.unregister()
    fkik.unregister()
    
if __name__ == "__main__":
    register()
