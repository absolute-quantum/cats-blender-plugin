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
    'version': (0, 12, 2),  # Has to be (x, x, x) not [x, x, x]!! # Only change this version and the dev branch var right before publishing the new update!
    'blender': (2, 80, 0),
    'wiki_url': 'https://github.com/michaeldegroot/cats-blender-plugin',
    'tracker_url': 'https://github.com/michaeldegroot/cats-blender-plugin/issues',
    'warning': '',
}
dev_branch = False

import os
import sys

# Append files to sys path
file_dir = os.path.dirname(__file__)
if file_dir not in sys.path:
    sys.path.append(file_dir)

import copy
import shutil
import pathlib
import requests
import addon_utils

import globs

# Check if cats is reloading or started fresh
if "bpy" not in locals():
    import bpy
    is_reloading = False
else:
    is_reloading = True

# Don't allow Blender versions older than 2.75
if bpy.app.version < (2, 75):
    sys.tracebacklimit = 0
    raise ImportError('\n\nThis Blender version is not supported by Cats. '
                      '\nPlease use Blender 2.79 or later.')

# Load or reload all cats modules
if not is_reloading:
    # This order is important
    import updater
    import mmd_tools_local
    import tools
    import ui
    import extentions
else:
    import importlib
    importlib.reload(updater)
    importlib.reload(mmd_tools_local)
    importlib.reload(tools)
    importlib.reload(ui)
    importlib.reload(extentions)


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


def remove_corrupted_files():
    to_remove = [
        'googletrans',
        'mmd_tools_local',
        'resources',
        'tests',
        'tools',
        'ui',
        '.gitignore',
        '.travis.yml',
        'LICENSE',
        'README.md',
        '__init__.py',
        'addon_updater.py',
        'addon_updater_ops.py',
        'extensions.py',
        'globs.py',
        'updater.py',
    ]

    no_perm = False
    os_error = False
    wrong_path = False
    faulty_installation = False
    main_dir = str(pathlib.Path(os.path.dirname(__file__)).resolve())

    if main_dir.endswith('addons'):
        print(os.path.dirname(__file__))
        print(main_dir)
        print('Wrong installation path')
        wrong_path = True
    else:
        main_dir = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve())

    print('Checking for CATS files in the addon directory:\n' + main_dir)
    files = [f for f in os.listdir(main_dir) if os.path.isfile(os.path.join(main_dir, f))]
    folders = [f for f in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, f))]

    for file in files:
        if file in to_remove:
            file_path = os.path.join(main_dir, file)
            try:
                os.remove(file_path)
                faulty_installation = True
                print('REMOVED', file)
            except PermissionError:
                no_perm = True
                print("Permissions: Failed to remove file " + file)
            except OSError:
                os_error = True
                print("OS: Failed to remove file " + file)

    for folder in folders:
        if folder in to_remove:
            folder_path = os.path.join(main_dir, folder)
            try:
                shutil.rmtree(folder_path)
                faulty_installation = True
                print('REMOVED', folder)
            except PermissionError:
                no_perm = True
                print("Permissions: Failed to remove folder " + folder)
            except OSError:
                os_error = True
                print("Failed to remove folder " + folder)

    if no_perm:
        sys.tracebacklimit = 0
        raise ImportError('                                                                                                                                                                                    '
                          '                     '
                          '\n\nFaulty CATS installation found!                                                                Faulty CATS installation found!'
                          '\nTo fix this restart Blender as admin!                                                        To fix this restart Blender as admin!'
                          '\n\n\n\n\nFaulty CATS installation found!'
                          '\nTo fix this restart Blender as admin!'
                          '\n\n\n\n\nFaulty CATS installation found!'
                          '\nTo fix this restart Blender as admin!'
                          '\n\n\n')

    if os_error:
        sys.tracebacklimit = 0
        message = '                                                                                                                                                                                    ' \
                  '                     '\
                  '\n\nFaulty CATS installation found!' \
                  '\nTo fix this delete the following files and folders inside your addons folder:' \
                  '\n'

        for folder in folders:
            if folder not in to_remove:
                message += "\n- " + os.path.join(main_dir, folder)

        for file in files:
            if file not in to_remove:
                message += "\n- " + os.path.join(main_dir, file)

        raise ImportError(message)

    if wrong_path:
        sys.tracebacklimit = 0
        raise ImportError('                                                                                                                                                                                    '
                          '                     '
                          '\n\nFaulty CATS installation found!                                                                   Faulty CATS installation found!'
                          '\nPlease install CATS via User Preferences and restart Blender!                 Please install CATS via User Preferences and restart Blender!'
                          '\n\n\n\n\nFaulty installation found!'
                          '\nPlease install CATS via User Preferences and restart Blender!'
                          '\n\n\n\n\nFaulty installation found!'
                          '\nPlease install CATS via User Preferences and restart Blender!'
                          '\n\n\n')

    if faulty_installation:
        sys.tracebacklimit = 0
        raise ImportError('                                                                                                                                                                                    '
                          '                     '
                          '\n\nFaulty CATS installation was found and fixed!                                                             Faulty CATS installation was found and fixed!'
                          '\nPlease restart Blender and enable CATS again!                                                           Please restart Blender and enable CATS again!'
                          '\n\n\n\n\nFaulty CATS installation was found and fixed!'
                          '\nPlease restart Blender and enable CATS again!'
                          '\n\n\n\n\nFaulty CATS installation was found and fixed!'
                          '\nPlease restart Blender and enable CATS again!'
                          '\n\n\n')


def set_cats_version_string():
    version = bl_info.get('version')
    version_temp = []
    version_str = ''

    for n in version:
        version_temp.append(n)

    if len(version_temp) > 0:
        # if in dev version, increase version
        if dev_branch:
            version_temp[len(version_temp)-1] += 1

        # Convert version to string
        version_str += str(version_temp[0])
        for index, i in enumerate(version_temp):
            if index == 0:
                continue
            version_str += '.' + str(version_temp[index])

    # Add -dev if in dev version
    if dev_branch:
        version_str += '-dev'

    return version_str


def register():
    print("\n### Loading CATS...")

    # Check for faulty CATS installations
    remove_corrupted_files()

    # Set cats version string
    version_str = set_cats_version_string()

    # Register Updater and check for CATS update
    print("Loading Updater..")
    updater.register(bl_info, dev_branch, version_str)

    # Set some global settings, first allowed use of globs
    globs.dev_branch = dev_branch
    globs.version_str = version_str

    # Load settings and show error if a faulty installation was deleted recently
    print("Loading settings..")
    show_error = False
    try:
        tools.settings.load_settings()
    except FileNotFoundError:
        show_error = True
    if show_error:
        sys.tracebacklimit = 0
        raise ImportError('                                                                                                                                                                                    '
                          '                     '
                          '\n\nPlease restart Blender and enable CATS again!                                                            Please restart Blender and enable CATS again!'
                          '\n\n\n\nPlease restart Blender and enable CATS again!'
                          '\n\n\n\nPlease restart Blender and enable CATS again!'
                          '\n\n\n\nPlease restart Blender and enable CATS again!'
                          '\n\n\n\n')

    # if not tools.settings.use_custom_mmd_tools():
    #     bpy.utils.unregister_module("mmd_tools")

    # Load mmd_tools
    print("Loading mmd_tools..")
    try:
        mmd_tools_local.register()
    except AttributeError:
        print('Could not register local mmd_tools')
        pass

    # Register all classes
    print('Registering CATS classes..')
    count = 0
    tools.register.order_classes()
    for cls in tools.register.__bl_classes:  # TODO ordered
        # print(cls)
        bpy.utils.register_class(cls)
        count += 1
    print('Registered', count, 'CATS classes.')

    # Register Scene types
    print("Registering scene types..")
    extentions.register()

    # Load supporter and settings icons and buttons
    print("Loading other stuff..")
    tools.supporter.load_other_icons()
    tools.supporter.load_supporters()
    tools.supporter.register_dynamic_buttons()

    # Load the dictionaries and check if they are found
    globs.dict_found = tools.translate.load_translations()

    # Set preferred Blender options
    if bpy.app.version < (2, 8):
        tools.common.get_user_preferences().system.use_international_fonts = True
    else:
        tools.common.get_user_preferences().view.use_international_fonts = True
    tools.common.get_user_preferences().filepaths.use_file_compression = True

    # Add shapekey button to shapekey menu
    bpy.types.MESH_MT_shape_key_specials.append(tools.shapekey.addToShapekeyMenu)

    # Disable request warning when using google translate
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # Apply the settings after a short time, because you can't change checkboxes during register process
    tools.settings.start_apply_settings_timer()

    print("### Loaded CATS successfully!\n")


def unregister():
    print("### Unloading CATS...")

    # Unregister updater
    updater.unregister()

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

    # Unregister all dynamic buttons and icons
    tools.supporter.unregister_dynamic_buttons()
    tools.supporter.unload_icons()

    # Remove shapekey button from shapekey menu
    bpy.types.MESH_MT_shape_key_specials.remove(tools.shapekey.addToShapekeyMenu)

    print("### Unloaded CATS successfully!\n")


if __name__ == '__main__':
    register()
