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

# Code author: Hotox
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats

import bpy
import os
import json
import json.decoder
import pathlib
import zipfile
import urllib.request
import urllib.error
import shutil
import webbrowser
import tools.common
from datetime import datetime
from threading import Thread
from pprint import pprint

# global variables
preview_collections = {}
supporter_data = None
settings_data = None
reloading = False
button_list = []

time_format = "%Y-%m-%d %H:%M:%S"

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")


class PatreonButton(bpy.types.Operator):
    bl_idname = 'supporter.patreon'
    bl_label = 'Become a Patron'

    def execute(self, context):
        webbrowser.open('https://www.patreon.com/catsblenderplugin')

        self.report({'INFO'}, 'Patreon page opened')
        return {'FINISHED'}


class ReloadButton(bpy.types.Operator):
    bl_idname = 'supporter.reload'
    bl_label = 'Reload List'
    bl_description = 'Reloads the supporter list'

    @classmethod
    def poll(cls, context):
        return not reloading

    def execute(self, context):
        global reloading
        reloading = True

        thread = Thread(target=download_file, args=[])
        thread.start()

        return {'FINISHED'}


class DynamicPatronButton(bpy.types.Operator):
    bl_idname = 'support.dynamic_patron_button'
    bl_label = 'Supporter Name'
    bl_description = 'This is an awesome supporter'

    website = None

    def execute(self, context):
        if self.website:
            webbrowser.open(self.website)
        return {'FINISHED'}


def register_dynamic_buttons():
    if not supporter_data:
        return

    temp_idnames = []
    for supporter in supporter_data.get('supporters'):
        name = supporter.get('displayname')
        idname = 'support.' + ''.join(filter(str.isalpha, name.lower()))

        description = name + ' is an awesome supporter'
        if supporter.get('description'):
            # description = name + ' says:\n\n' + supporter.get('description') + '\n'
            description = supporter.get('description') + '\n'

        website = None
        if supporter.get('website'):
            website = supporter.get('website')

        while idname in temp_idnames:
            idname += '2'

        button = type('DynOp_' + name, (DynamicPatronButton, ),
                  {'bl_idname': idname,
                   'bl_label': name,
                   'bl_description': description,
                   'website': website
                   })

        button_list.append(button)
        supporter['idname'] = idname
        temp_idnames.append(idname)
        bpy.utils.register_class(button)


def unregister_dynamic_buttons():
    for button in button_list:
        try:
            bpy.utils.unregister_class(button)
        except RuntimeError:
            pass

    button_list.clear()


def download_file():
    # Load all the directories and files
    downloads_dir = os.path.join(resources_dir, "downloads")
    extracted_zip_dir = os.path.join(downloads_dir, "cats_supporter_list-master")
    icons_dir = os.path.join(resources_dir, "icons")
    icons_supporter_dir = os.path.join(icons_dir, "supporters")

    supporter_zip_file = os.path.join(downloads_dir, "cats_supporter_list.zip")
    supporter_list_file = os.path.join(resources_dir, "supporters.json")

    extracted_supporter_list_file = os.path.join(extracted_zip_dir, "supporters.json")
    extracted_icons_dir = os.path.join(extracted_zip_dir, "supporters")

    # Create download folder
    pathlib.Path(downloads_dir).mkdir(exist_ok=True)

    # Download zip
    print('DOWNLOAD FILE')
    try:
        urllib.request.urlretrieve("https://github.com/Darkblader24/cats_supporter_list/archive/master.zip", supporter_zip_file)
    except urllib.error.URLError:
        print("FILE COULD NOT BE DOWNLOADED")
        shutil.rmtree(downloads_dir)
        return
    print('DOWNLOAD FINISHED')

    # If zip is not downloaded, abort
    if not os.path.isfile(supporter_zip_file):
        print("ZIP NOT FOUND!")
        shutil.rmtree(downloads_dir)
        return

    # Extract the downloaded zip
    print('EXTRACTING ZIP')
    with zipfile.ZipFile(supporter_zip_file, "r") as zip_ref:
        zip_ref.extractall(downloads_dir)
    print('EXTRACTED')

    # If zip is not extracted, abort
    if not os.path.isdir(extracted_zip_dir):
        print("EXTRACTED ZIP FOLDER NOT FOUND!")
        shutil.rmtree(downloads_dir)
        return

    # delete existing supporter list and icon folder
    if os.path.isfile(supporter_list_file):
        print("REMOVED SUPPORT LIST")
        os.remove(supporter_list_file)
    if os.path.isdir(icons_supporter_dir):
        print("REMOVED ICON DIR")
        shutil.rmtree(icons_supporter_dir)

    # Move the extracted files to their correct places
    shutil.move(extracted_supporter_list_file, supporter_list_file)
    shutil.move(extracted_icons_dir, icons_dir)

    # Delete download folder
    shutil.rmtree(downloads_dir)

    # Save update time in settings
    settings_data['last_supporter_update'] = datetime.now().strftime(time_format)
    save_settings()

    # Reload supporters
    reload_supporters()


def readJson():
    supporters_file = os.path.join(resources_dir, "supporters.json")

    print('READING FILE')

    if not os.path.isfile(supporters_file):
        print("SUPPORTER LIST FILE NOT FOUND!")
        return

    print("SUPPORTER LIST FILE FOUND!")
    try:
        with open(supporters_file) as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        return

    global supporter_data
    supporter_data = data


def load_supporters():
    global reloading

    now = datetime.now()
    if not settings_data \
            or not settings_data.get('last_supporter_update') \
            or tools.common.days_between(now.strftime(time_format), settings_data.get('last_supporter_update'), time_format) > 1:
        # Start asynchronous download of supporter list zip                                # These are the started days.
        reloading = True                                                                   # So >2 equals 2 full days
        thread = Thread(target=download_file, args=[])
        thread.start()

    # Read existing supporter list
    readJson()

    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    icons_dir = os.path.join(resources_dir, "icons")
    icons_supporter_dir = os.path.join(icons_dir, "supporters")

    # load the supporters icons
    if supporter_data:
        for supporter in supporter_data['supporters']:
            name = supporter['displayname']
            try:
                pcoll.load(name, os.path.join(icons_supporter_dir, name + '.png'), 'IMAGE')
            except KeyError:
                pass
        for news in supporter_data['news']:
            custom_icon = news.get('custom_icon')
            if not custom_icon or custom_icon in pcoll:
                continue
            try:
                pcoll.load(custom_icon, os.path.join(icons_supporter_dir, custom_icon + '.png'), 'IMAGE')
            except KeyError:
                pass

    if preview_collections.get('supporter_icons'):
        bpy.utils.previews.remove(preview_collections['supporter_icons'])
    preview_collections['supporter_icons'] = pcoll


def reload_supporters():
    # Read the support file
    readJson()

    # Get existing preview collection or create new one
    if preview_collections.get('supporter_icons'):
        pcoll = preview_collections['supporter_icons']
    else:
        pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    icons_dir = os.path.join(resources_dir, "icons")
    icons_supporter_dir = os.path.join(icons_dir, "supporters")

    # load the supporters icons
    if supporter_data:
        for supporter in supporter_data['supporters']:
            name = supporter['displayname']

            if name in pcoll:
                continue

            try:
                pcoll.load(name, os.path.join(icons_supporter_dir, name + '.png'), 'IMAGE')
            except KeyError:
                pass
        for news in supporter_data['news']:
            custom_icon = news.get('custom_icon')
            if not custom_icon or custom_icon in pcoll:
                continue

            try:
                pcoll.load(custom_icon, os.path.join(icons_supporter_dir, custom_icon + '.png'), 'IMAGE')
            except KeyError:
                pass

    if not preview_collections.get('supporter_icons'):
        preview_collections['supporter_icons'] = pcoll

    unregister_dynamic_buttons()
    register_dynamic_buttons()

    # Set running false
    global reloading
    reloading = False

    # Refresh ui because of async running
    ui_refresh()


def load_other_icons():
    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    icons_dir = os.path.join(resources_dir, "icons")
    icons_other_dir = os.path.join(icons_dir, "other")

    # load a preview thumbnail of a file and store in the previews collection
    pcoll.load('heart1', os.path.join(icons_other_dir, 'heart1.png'), 'IMAGE')
    pcoll.load('discord1', os.path.join(icons_other_dir, 'discord1.png'), 'IMAGE')
    pcoll.load('cats1', os.path.join(icons_other_dir, 'cats1.png'), 'IMAGE')
    pcoll.load('empty', os.path.join(icons_other_dir, 'empty.png'), 'IMAGE')
    pcoll.load('UP_ARROW', os.path.join(icons_other_dir, 'blender_up_arrow.png'), 'IMAGE')
    pcoll.load('TRANSLATE', os.path.join(icons_other_dir, 'translate.png'), 'IMAGE')

    preview_collections['custom_icons'] = pcoll


def unload_icons():
    print('UNLOADING ICONS!')
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    print('DONE!')


def ui_refresh():
    # A way to refresh the ui
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                area.tag_redraw()


def load_settings():
    print('READING SETTINGS FILE')
    global settings_data
    settings_data = read_settings_file()

    pprint(settings_data)


def save_settings():
    settings_file = os.path.join(resources_dir, "settings.json")

    with open(settings_file, 'w') as outfile:
        json.dump(settings_data, outfile)


def read_settings_file():
    settings_file = os.path.join(resources_dir, "settings.json")

    # default data
    data_default = {
        'last_supporter_update': None
    }

    # Check for existing settings file
    if not os.path.isfile(settings_file):
        print("SETTINGS LIST FILE NOT FOUND!")
        with open(settings_file, 'w') as outfile:
            json.dump(data_default, outfile)
        return data_default

    # Read settings and recreate it if error  is found
    try:
        with open(settings_file) as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN SETTINGS FILE")
        os.remove(settings_file)
        return read_settings_file()

    # Check for unwanted settings entries
    changed = False
    remove_list = []
    for key in data.keys():
        if key not in data_default:
            remove_list.append(key)

    # Remove unwanted settings
    for key in remove_list:
        data.pop(key, None)
        changed = True
        print('REMOVED', key)

    # Check for missing settings entries
    for key, value in data_default.items():
        if key not in data:
            data[key] = value
            changed = True
            print('ADDED', key)

    # Check if timestamps are correct
    if data.get('last_supporter_update'):
        try:
            datetime.strptime(data.get('last_supporter_update'), time_format)
        except ValueError:
            data['last_supporter_update'] = None
            changed = True
            print('RESET TIME')

    # If data changed, update settings file
    if changed:
        with open(settings_file, 'w') as outfile:
            json.dump(data, outfile)
        print('UPDATED MISSING SETTINGS')

    return data
