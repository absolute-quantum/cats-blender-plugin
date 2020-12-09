# -*- coding: utf-8 -*-

from bpy.types import Panel

from mmd_tools_local import register_wrap
from mmd_tools_local.core.model import Model
from mmd_tools_local.core.sdef import FnSDEF

class _PanelBase(object):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

@register_wrap
class MMDModelObjectDisplayPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_root_object_display'
    bl_label = 'MMD Display'

    @classmethod
    def poll(cls, context):
        return Model.findRoot(context.active_object)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        root = Model.findRoot(obj)

        row = layout.row(align=True)
        c = row.column(align=True)
        c.prop(root.mmd_root, 'show_meshes', text='Mesh')
        c.prop(root.mmd_root, 'show_armature', text='Armature')
        c.prop(root.mmd_root, 'show_rigid_bodies', text='Rigid Body')
        c.prop(root.mmd_root, 'show_joints', text='Joint')
        c = row.column(align=True)
        c.prop(root.mmd_root, 'show_temporary_objects', text='Temporary Object')
        c.label() # for alignment only
        c.prop(root.mmd_root, 'show_names_of_rigid_bodies', text='Rigid Body Name')
        c.prop(root.mmd_root, 'show_names_of_joints', text='Joint Name')

        row = layout.row(align=True)
        #row.active = context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}
        row.prop(root.mmd_root, 'use_toon_texture', text='Toon Texture')
        row.prop(root.mmd_root, 'use_sphere_texture', text='Sphere Texture')

        row = layout.row(align=True)
        row.prop(root.mmd_root, 'use_sdef', text='SDEF')

        layout.prop(root.mmd_root, 'use_property_driver', text='Property Drivers', icon='DRIVER')

        self.__draw_IK_toggle(Model(root).armature() or root)

    def __draw_IK_toggle(self, armature):
        bones = getattr(armature.pose, 'bones', ())
        ik_map = {bones[c.subtarget]:(b.bone, c.chain_count, not c.is_valid) for b in bones for c in b.constraints if c.type == 'IK' and c.subtarget in bones}
        if ik_map:
            base = sum(b.bone.length for b in ik_map.keys())/len(ik_map)*0.8
            groups = {}
            for ik, (b, cnt, err) in ik_map.items():
                if any(all(x) for x in zip(ik.bone.layers, armature.data.layers)):
                    px, py, pz = -ik.bone.head_local/base
                    bx, by, bz = -b.head_local/base*0.15
                    groups.setdefault((int(pz), int(bz), int(px**2), -cnt), set()).add(((px, -py, bx), ik)) # (px, pz, -py, bx, bz, -by)
            layout = self.layout.box().column()
            for _, group in sorted(groups.items()):
                row = layout.row()
                for _, ik in sorted(group, key=lambda x: x[0]):
                    ic = 'ERROR' if ik_map[ik][-1] else 'NONE'
                    row.prop(ik, 'mmd_ik_toggle', text=ik.name, toggle=True, icon=ic)

@register_wrap
class MMDViewPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_view'
    bl_label = 'MMD Shading'

    def draw(self, context):
        layout = self.layout

        c = layout.column(align=True)
        r = c.row(align=True)
        r.operator('mmd_tools.set_glsl_shading', text='GLSL')
        r.operator('mmd_tools.set_shadeless_glsl_shading', text='Shadeless')
        r = c.row(align=True)
        r.operator('mmd_tools.reset_shading', text='Reset')

@register_wrap
class MMDSDEFPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_sdef'
    bl_label = 'MMD SDEF Driver'

    def draw(self, context):
        c = self.layout.column(align=True)
        c.operator('mmd_tools.sdef_bind', text='Bind')
        c.operator('mmd_tools.sdef_unbind', text='Unbind')
        row = c.row()
        row.label(text='Cache Info: %d data'%(len(FnSDEF.g_verts)), icon='INFO')
        row.operator('mmd_tools.sdef_cache_reset', text='', icon='X')
