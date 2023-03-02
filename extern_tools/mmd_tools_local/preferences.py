# -*- coding: utf-8 -*-

import os

import bpy

from mmd_tools_local import operators


def _get_update_candidate_branches(_, __):
    updater = operators.addon_updater.AddonUpdaterManager.get_instance()
    if not updater.candidate_checked():
        return []

    return [(name, name, "") for name in updater.get_candidate_branch_names()]


class MMDToolsAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    enable_mmd_model_production_features: bpy.props.BoolProperty(
        name="Enable MMD Model Production Features",
        default=True,
    )
    shared_toon_folder: bpy.props.StringProperty(
        name="Shared Toon Texture Folder",
        description=('Directory path to toon textures. This is normally the "Data" directory within of your MikuMikuDance directory'),
        subtype='DIR_PATH',
        default=os.path.join(os.path.dirname(__file__), 'externals', 'MikuMikuDance'),
    )
    base_texture_folder: bpy.props.StringProperty(
        name='Base Texture Folder',
        description='Path for textures shared between models',
        subtype='DIR_PATH',
    )
    dictionary_folder: bpy.props.StringProperty(
        name='Dictionary Folder',
        description='Path for searching csv dictionaries',
        subtype='DIR_PATH',
        default=os.path.dirname(__file__),
    )

    # for add-on updater
    updater_branch_to_update: bpy.props.EnumProperty(
        name='Branch',
        description='Target branch to update add-on',
        items=_get_update_candidate_branches
    )

    def draw(self, _context):
        layout: bpy.types.UILayout = self.layout # pylint: disable=no-member
        layout.prop(self, "enable_mmd_model_production_features")
        layout.prop(self, "shared_toon_folder")
        layout.prop(self, "base_texture_folder")
        layout.prop(self, "dictionary_folder")

        # add-on updater
        update_col = layout.box().column(align=False)
        update_col.label(text='Add-on update', icon='RECOVER_LAST')
        updater = operators.addon_updater.AddonUpdaterManager.get_instance()

        if updater.updated():
            col = update_col.column()
            col.scale_y = 2
            col.alert = True
            col.operator(
                "wm.quit_blender",
                text="Restart Blender to complete update",
                icon="ERROR"
            )
            return

        if not updater.candidate_checked():
            col = update_col.column()
            col.scale_y = 2
            col.operator(
                operators.addon_updater.CheckAddonUpdate.bl_idname,
                text="Check mmd_tools add-on update",
                icon='FILE_REFRESH'
            )
        else:
            row = update_col.row(align=True)
            row.scale_y = 2
            col = row.column()
            col.operator(
                operators.addon_updater.CheckAddonUpdate.bl_idname,
                text="Check mmd_tools add-on update",
                icon='FILE_REFRESH'
            )
            col = row.column()
            if updater.update_ready():
                col.enabled = True
                col.operator(
                    operators.addon_updater.UpdateAddon.bl_idname,
                    text=bpy.app.translations.pgettext_iface("Update to the latest release version ({})").format(updater.latest_version()),
                    icon='TRIA_DOWN_BAR'
                ).branch_name = updater.latest_version()
            else:
                col.enabled = False
                col.operator(
                    operators.addon_updater.UpdateAddon.bl_idname,
                    text="No updates are available"
                )

            update_col.separator()
            update_col.label(text="(Danger) Manual Update:")
            row = update_col.row(align=True)
            row.prop(self, "updater_branch_to_update", text="Target")
            row.operator(
                operators.addon_updater.UpdateAddon.bl_idname, text="Update",
                icon='TRIA_DOWN_BAR'
            ).branch_name = self.updater_branch_to_update

            update_col.separator()
            if updater.has_error():
                box = update_col.box()
                box.label(text=updater.error(), icon='CANCEL')
            elif updater.has_info():
                box = update_col.box()
                box.label(text=updater.info(), icon='ERROR')
