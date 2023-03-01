# -*- coding: utf-8 -*-

import time

import bpy
from mmd_tools_local.core import model
from mmd_tools_local.core.sdef import FnSDEF


class MMDToolsSceneSetupPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_scene_setup'
    bl_label = 'Scene Setup'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    __LANGUAGE_MANUAL_URL = {
        'ja_JP': 'https://mmd-blender.fandom.com/ja/wiki/MMD_Tools/%E3%83%9E%E3%83%8B%E3%83%A5%E3%82%A2%E3%83%AB',
    }

    def draw(self, context: bpy.types.Context):
        self.layout.row(align=True).operator(
            'wm.url_open', text='MMD Tools/Manual', icon='URL'
        ).url = self.__LANGUAGE_MANUAL_URL.get(context.preferences.view.language, 'https://mmd-blender.fandom.com/wiki/MMD_Tools/Manual')

        self.draw_io()
        self.draw_timeline(context)
        self.draw_rigid_body(context)

    def draw_io(self):
        row = self.layout.row()
        col = row.column(align=True)
        col.label(text='Model:', icon='OUTLINER_OB_ARMATURE')
        col.operator('mmd_tools.import_model', text='Import')
        col.operator('mmd_tools.export_pmx', text='Export')

        col = row.column(align=True)
        col.label(text='Motion:', icon='ANIM')
        col.operator('mmd_tools.import_vmd', text='Import')
        col.operator('mmd_tools.export_vmd', text='Export')

        col = row.column(align=True)
        col.label(text='Pose:', icon='POSE_HLT')
        col.operator('mmd_tools.import_vpd', text='Import')
        col.operator('mmd_tools.export_vpd', text='Export')

    def draw_timeline(self, context):
        col = self.layout.column(align=True)
        row = col.row(align=False)
        row.label(text='Timeline:', icon='TIME')
        row.prop(context.scene, 'frame_current')
        row = col.row(align=True)
        row.prop(context.scene, 'frame_start', text='Start')
        row.prop(context.scene, 'frame_end', text='End')

    def draw_rigid_body(self, context):
        rigidbody_world = context.scene.rigidbody_world

        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=False)
        row.label(text='Rigid Body Physics:', icon='PHYSICS')
        row.row().operator(
            'mmd_tools.rigid_body_world_update',
            text='Update World',
            icon='NONE' if getattr(rigidbody_world, 'substeps_per_frame', 0) == 1 else 'ERROR'
        )

        if rigidbody_world:
            row = col.row(align=True)
            row.prop(rigidbody_world, 'substeps_per_frame', text='Substeps')
            row.prop(rigidbody_world, 'solver_iterations', text='Iterations')

            point_cache = rigidbody_world.point_cache

            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = not point_cache.is_baked
            row.prop(point_cache, 'frame_start')
            row.prop(point_cache, 'frame_end')

            row = col.row(align=True)
            if point_cache.is_baked is True:
                row.operator("mmd_tools.ptcache_rigid_body_delete_bake", text="Delete Bake")
            else:
                row.operator("mmd_tools.ptcache_rigid_body_bake", text="Bake")


class MMDToolsModelSetupPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_model_setup'
    bl_label = 'Model Setup'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    def draw(self, context: bpy.types.Context):
        active_object: bpy.types.Object = context.active_object
        mmd_root_object = model.Model.findRoot(active_object)

        if mmd_root_object is None:
            self.layout.label(text='Select a MMD Model')
            return

        col = self.layout.column(align=True)
        col.label(text=mmd_root_object.mmd_root.name, icon='OUTLINER_OB_ARMATURE')

        self.draw_visibility(context, mmd_root_object)
        self.draw_assembly(context, mmd_root_object)
        self.draw_ik_toggle(context, mmd_root_object)
        self.draw_mesh(context, mmd_root_object)
        self.draw_material(context, mmd_root_object)
        self.draw_misc(context, mmd_root_object)

    def draw_visibility(self, context, mmd_root_object):
        col = self.layout.column(align=True)
        row = col.row(align=False)
        row.label(text='Visibility:', icon='HIDE_OFF')
        row.operator('mmd_tools.reset_object_visibility', text='Reset')

        mmd_root = mmd_root_object.mmd_root
        row = col.row(align=False)
        cell = row.row(align=True)
        cell.prop(mmd_root, 'show_meshes', toggle=True, text='Mesh', icon='MESH_DATA')
        cell.prop(mmd_root, 'show_armature', toggle=True, text='Armature', icon='ARMATURE_DATA')
        cell.prop(mmd_root, 'show_temporary_objects', toggle=True, text='Temporary Object', icon='EMPTY_AXIS')
        cell = row.row(align=True)
        cell.prop(mmd_root, 'show_rigid_bodies', toggle=True, text='Rigid Body', icon='RIGID_BODY')
        cell.prop(mmd_root, 'show_names_of_rigid_bodies', toggle=True, icon_only=True, icon='SHORTDISPLAY')
        cell = row.row(align=True)
        cell.prop(mmd_root, 'show_joints', toggle=True, text='Joint', icon='RIGID_BODY_CONSTRAINT')
        cell.prop(mmd_root, 'show_names_of_joints', toggle=True, icon_only=True, icon='SHORTDISPLAY')

    def draw_assembly(self, context, mmd_root_object):
        col = self.layout.column(align=False)
        row = col.row(align=True)
        row.label(text='Assembly:', icon='MODIFIER_ON')

        grid = col.grid_flow(row_major=True)

        row = grid.row(align=True)
        row.operator('mmd_tools.assemble_all', text='All', icon='SETTINGS')
        row.operator('mmd_tools.disassemble_all', text='', icon='TRASH')

        row = grid.row(align=True)
        row.operator('mmd_tools.sdef_bind', text='SDEF', icon='MOD_SIMPLEDEFORM')
        if len(FnSDEF.g_verts) > 0:
            row.operator('mmd_tools.sdef_cache_reset', text='', icon='FILE_REFRESH')
        row.operator('mmd_tools.sdef_unbind', text='', icon='TRASH')

        row = grid.row(align=True)
        row.operator('mmd_tools.apply_additional_transform', text='Bone', icon='CONSTRAINT_BONE')
        row.operator('mmd_tools.clean_additional_transform', text='', icon='TRASH')

        row = grid.row(align=True)
        row.operator('mmd_tools.morph_slider_setup', text='Morph', icon='SHAPEKEY_DATA').type = 'BIND'
        row.operator('mmd_tools.morph_slider_setup', text='', icon='TRASH').type = 'UNBIND'

        row = grid.row(align=True)
        row.active = getattr(context.scene.rigidbody_world, 'enabled', False)

        mmd_root = mmd_root_object.mmd_root
        if not mmd_root.is_built:
            row.operator('mmd_tools.build_rig', text='Physics', icon='PHYSICS', depress=False)
        else:
            row.operator('mmd_tools.clean_rig', text='Physics', icon='PHYSICS', depress=True)

        row = grid.row(align=True)
        row.prop(mmd_root, 'use_property_driver', text='Property', toggle=True, icon='DRIVER')

    __toggle_items_ttl = 0.0
    __toggle_items_cache = None

    def __get_toggle_items(self, mmd_root_object: bpy.types.Object):
        if self.__toggle_items_ttl > time.time():
            return self.__toggle_items_cache

        self.__toggle_items_ttl = time.time() + 10
        self.__toggle_items_cache = []
        armature_object = model.FnModel.find_armature(mmd_root_object)
        pose_bones = armature_object.pose.bones
        ik_map = {
            pose_bones[c.subtarget]: (b.bone, c.chain_count, not c.is_valid)
            for b in pose_bones
            for c in b.constraints
            if c.type == 'IK' and c.subtarget in pose_bones
        }

        if not ik_map:
            return self.__toggle_items_cache

        base = sum(b.bone.length for b in ik_map.keys())/len(ik_map)*0.8

        groups = {}
        for ik, (b, cnt, err) in ik_map.items():
            if any(all(x) for x in zip(ik.bone.layers, armature_object.data.layers)):
                px, py, pz = -ik.bone.head_local/base
                bx, by, bz = -b.head_local/base*0.15
                groups.setdefault(
                    (int(pz), int(bz), int(px**2), -cnt), set()
                ).add(((px, -py, bx), ik))  # (px, pz, -py, bx, bz, -by)

        for _, group in sorted(groups.items()):
            for _, ik in sorted(group, key=lambda x: x[0]):
                ic = 'ERROR' if ik_map[ik][-1] else 'NONE'
                self.__toggle_items_cache.append((ik, ic))

        return self.__toggle_items_cache

    def draw_ik_toggle(self, _context, mmd_root_object):
        col = self.layout.column(align=True)
        row = col.row(align=False)
        row.label(text='IK Toggle:', icon='CON_KINEMATIC')
        grid = col.grid_flow(row_major=True, align=True)

        for ik, ic in self.__get_toggle_items(mmd_root_object):
            grid.row(align=True).prop(ik, 'mmd_ik_toggle', text=ik.name, toggle=True, icon=ic)

    def draw_mesh(self, context, mmd_root_object):
        col = self.layout.column(align=True)
        col.label(text='Mesh:', icon='MESH_DATA')
        grid = col.grid_flow(row_major=True, align=True)
        grid.row(align=True).operator('mmd_tools.separate_by_materials', text='Separate by Materials', icon='MOD_EXPLODE')
        grid.row(align=True).operator('mmd_tools.join_meshes', text='Join', icon='MESH_CUBE')

    def draw_material(self, context, mmd_root_object):
        col = self.layout.column(align=True)
        col.label(text='Material:', icon='MATERIAL')

        grid = col.grid_flow(row_major=True, align=False)
        row = grid.row(align=True)
        row.prop(mmd_root_object.mmd_root, 'use_toon_texture', text='Toon Texture', toggle=True, icon='SHADING_RENDERED')
        row.prop(mmd_root_object.mmd_root, 'use_sphere_texture', text='Sphere Texture', toggle=True, icon='MATSPHERE')
        row = grid.row(align=True)
        row.operator('mmd_tools.edge_preview_setup', text='Edge Preview', icon='ANTIALIASED').action = 'CREATE'
        row.operator('mmd_tools.edge_preview_setup', text='', icon='TRASH').action = 'CLEAN'
        row = grid.row(align=True)
        row.operator('mmd_tools.convert_materials', text='Convert to Blender', icon='BLENDER')

    def draw_misc(self, context, mmd_root_object):
        col = self.layout.column(align=True)
        col.label(text='Misc:', icon='TOOL_SETTINGS')
        grid = col.grid_flow(row_major=True)
        grid.row(align=True).operator('mmd_tools.global_translation_popup', text='(Experimental) Global Translation')
        grid.row(align=True).operator('mmd_tools.change_mmd_ik_loop_factor', text='Change MMD IK Loop Factor')
