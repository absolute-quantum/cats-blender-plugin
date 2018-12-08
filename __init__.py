# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats, Hotox

bl_info = {
    'name': 'Cats Blender Plugin',
    'category': '3D View',
    'author': 'GiveMeAllYourCats',
    'location': 'View 3D > Tool Shelf > CATS',
    'description': 'A tool designed to shorten steps needed to import and optimize models into VRChat',
    'version': [0, 12, 0],  # Only change this version and the dev branch var right before publishing the new update!
    'blender': (2, 80, 0),
    'wiki_url': 'https://github.com/michaeldegroot/cats-blender-plugin',
    'tracker_url': 'https://github.com/michaeldegroot/cats-blender-plugin/issues',
    'warning': '',
}

import os
import sys

# Append files to sys path
file_dir = os.path.dirname(__file__)
if file_dir not in sys.path:
    sys.path.append(file_dir)

import copy
import globs
import requests
import extend_types

# Load package name, important for updater
globs.package = __package__

# Check if cats is reloading or started fresh
if "bpy" not in locals():
    import bpy
    globs.is_reloading = False
else:
    globs.is_reloading = True

if not globs.is_reloading:
    import mmd_tools_local
    import addon_updater_ops

    # This order is important
    import tools
    import ui
else:
    import importlib
    importlib.reload(mmd_tools_local)
    importlib.reload(addon_updater_ops)
    importlib.reload(tools)
    importlib.reload(ui)


# How to update mmd_tools:
# Paste mmd_tools folder into project
# Delete mmd_tools_local folder
# Refactor folder name "mmd_tools" to "mmd_tools_local"
# Search for "show_backface_culling" and set it to False in view.py
# Done

# How to update googletrans:
# in the gtoken.py on line 57 update this line to include "verify=False":
# r = self.session.get(self.host, verify=False)
# In client.py on line 42 remove the Hyper part, it's not faster at all!
# Just comment it out.
# Also see pull request for TKK change
# Also wm progress in client.py
# Done

# How to set up PyCharm with Blender:
# https://b3d.interplanety.org/en/using-external-ide-pycharm-for-writing-blender-scripts/

globs.dev_branch = False
globs.version = copy.deepcopy(bl_info.get('version'))


def register():
    print("\n### Loading CATS...")

    # Load settings
    tools.settings.load_settings()

    # if not tools.settings.use_custom_mmd_tools():
    #     bpy.utils.unregister_module("mmd_tools")

    # Load mmd_tools
    try:
        mmd_tools_local.register()
    except AttributeError:
        print('Could not register local mmd_tools')
        pass

    # Register updater
    try:
        addon_updater_ops.register(bl_info)
    except ValueError:
        print('Error while registering updater.')
        pass

    # Register all classes
    count = 0
    tools.register.order_classes()
    for cls in tools.register.__bl_ordered_classes:
        # print(cls)
        bpy.utils.register_class(cls)
        count += 1
    print('Registered', count, 'CATS classes.')

    # Register Scene types
    extend_types.register()

    # Set cats version string
    tools.common.set_cats_verion_string()

    # Load supporter and settings icons and buttons
    tools.supporter.load_other_icons()
    tools.supporter.load_supporters()
    tools.supporter.register_dynamic_buttons()

    # Load the dictionaries and check if they are found
    globs.dict_found = tools.translate.load_translations()

    # Set preferred Blender options
    bpy.context.user_preferences.system.use_international_fonts = True
    bpy.context.user_preferences.filepaths.use_file_compression = True

    # Add shapekey button to shapekey menu
    bpy.types.MESH_MT_shape_key_specials.append(tools.shapekey.addToShapekeyMenu)

    # Disable request warning when using google translate
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # Apply the settings after a short time, because you can't change checkboxes during register process
    tools.settings.start_apply_settings_timer()

    print("### Loaded CATS successfully!")


def unregister():
    print("### Unloading CATS...")
    # # Unload mmd_tools
    try:
        mmd_tools_local.unregister()
    except AttributeError:
        print('Could not unregister local mmd_tools')
        pass

    # Unload all classes in reverse order
    count = 0
    for cls in reversed(tools.register.__bl_ordered_classes):
        bpy.utils.unregister_class(cls)
        count += 1
    print('Unregistered', count, 'CATS classes.')

    # Unload the updater
    addon_updater_ops.unregister()

    # Unregister all dynamic buttons and icons
    tools.supporter.unregister_dynamic_buttons()
    tools.supporter.unload_icons()

    # Remove shapekey button from shapekey menu
    bpy.types.MESH_MT_shape_key_specials.remove(tools.shapekey.addToShapekeyMenu)

    print("### Unloaded CATS successfully!")


if __name__ == '__main__':
    register()
