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

import os
import bpy
import json
import shutil
import pathlib
import zipfile
import webbrowser
import json.decoder
import urllib.error
import urllib.request

from threading import Thread
from datetime import datetime, timezone
from bpy.utils import previews


from . import common as Common
from . import settings as Settings
from .. import globs
from ..tools.register import register_wrap
from ..translations import t

# global variables
preview_collections = {}
supporter_data = None
reloading = False
auto_updated = False
button_list = []
last_update = None

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")


@register_wrap
class PatreonButton(bpy.types.Operator):
    bl_idname = 'cats_supporter.patreon'
    bl_label = t('PatreonButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('PatreonButton.URL'))

        self.report({'INFO'}, t('PatreonButton.success'))
        return {'FINISHED'}


@register_wrap
class ReloadButton(bpy.types.Operator):
    bl_idname = 'cats_supporter.reload'
    bl_label = t('ReloadButton.label')
    bl_description = t('ReloadButton.desc')
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return not reloading

    def execute(self, context):
        check_for_update_background(force_update=True)
        return {'FINISHED'}


@register_wrap
class DynamicPatronButton(bpy.types.Operator):
    bl_idname = 'cats_supporter.dynamic_patron_button'
    bl_label = t('DynamicPatronButton.label')
    bl_description = t('DynamicPatronButton.desc')
    bl_options = {'INTERNAL'}

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
        if supporter.get('disabled'):
            continue

        name = supporter.get('displayname')
        idname = 'support.' + ''.join(filter(str.isalpha, name.lower()))

        description = t('register_dynamic_buttons.desc', name=name)
        if supporter.get('description'):
            # description = name + ' says:\n\n' + supporter.get('description') + '\n'
            description = supporter.get('description')

        website = None
        if supporter.get('website'):
            website = supporter.get('website')

        while idname in temp_idnames:
            idname += '2'

        button = type('DynOp_' + name, (DynamicPatronButton, ),
                  {'bl_idname': idname,
                   'bl_label': name,
                   'bl_description': description,
                   'bl_options': {'INTERNAL'},
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
    # print('DOWNLOAD FILE')
    try:
        urllib.request.urlretrieve("https://github.com/Darkblader24/cats_supporter_list/archive/master.zip", supporter_zip_file)
    except urllib.error.URLError:
        print("FILE COULD NOT BE DOWNLOADED")
        shutil.rmtree(downloads_dir)
        finish_reloading()
        return
    # print('DOWNLOAD FINISHED')

    # If zip is not downloaded, abort
    if not os.path.isfile(supporter_zip_file):
        print("ZIP NOT FOUND!")
        shutil.rmtree(downloads_dir)
        finish_reloading()
        return

    # Extract the downloaded zip
    # print('EXTRACTING ZIP')
    with zipfile.ZipFile(supporter_zip_file, "r") as zip_ref:
        zip_ref.extractall(downloads_dir)
    # print('EXTRACTED')

    # If zip is not extracted, abort
    if not os.path.isdir(extracted_zip_dir):
        print("EXTRACTED ZIP FOLDER NOT FOUND!")
        shutil.rmtree(downloads_dir)
        finish_reloading()
        return

    # delete existing supporter list and icon folder
    if os.path.isfile(supporter_list_file):
        # print("REMOVED SUPPORT LIST")
        os.remove(supporter_list_file)
    if os.path.isdir(icons_supporter_dir):
        # print("REMOVED ICON DIR")
        shutil.rmtree(icons_supporter_dir)

    # Move the extracted files to their correct places
    shutil.move(extracted_supporter_list_file, supporter_list_file)
    shutil.move(extracted_icons_dir, icons_dir)

    # Delete download folder
    shutil.rmtree(downloads_dir)

    # Save update time in settings
    Settings.set_last_supporter_update(last_update)

    # Reload supporters
    reload_supporters()


def readJson():
    supporters_file = os.path.join(resources_dir, "supporters.json")

    # print('READING FILE')

    if not os.path.isfile(supporters_file):
        print("SUPPORTER LIST FILE NOT FOUND!")
        return

    # print("SUPPORTER LIST FILE FOUND!")
    try:
        with open(supporters_file, encoding="utf8") as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        print("JSON COULD NOT BE READ")
        return

    global supporter_data
    supporter_data = data


def load_supporters():
    # Read existing supporter list
    readJson()

    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    pcoll = bpy.utils.previews.new()

    # load the supporters and news icons
    load_icons(pcoll)

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

    # load the supporters and news icons
    load_icons(pcoll)

    if not preview_collections.get('supporter_icons'):
        preview_collections['supporter_icons'] = pcoll

    unregister_dynamic_buttons()
    register_dynamic_buttons()

    # Finish reloading
    finish_reloading()
    print('Updated supporter list.')


def load_icons(pcoll):
    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    icons_dir = os.path.join(resources_dir, "icons")
    icons_supporter_dir = os.path.join(icons_dir, "supporters")

    if supporter_data:
        for supporter in supporter_data['supporters']:
            if supporter.get('disabled'):
                continue

            name = supporter['displayname']
            iconname = supporter.get('iconname')

            if not iconname:
                iconname = name

            if name in pcoll:
                continue

            try:
                pcoll.load(name, os.path.join(icons_supporter_dir, iconname + '.png'), 'IMAGE')
            except KeyError:
                pass

        for news in supporter_data['news']:
            custom_icon = news.get('custom_icon')

            if news.get('disabled') or not news.get('info') or not custom_icon or custom_icon in pcoll:
                continue

            try:
                pcoll.load(custom_icon, os.path.join(icons_supporter_dir, custom_icon + '.png'), 'IMAGE')
            except KeyError:
                pass


def finish_reloading():
    # Set running false
    global reloading
    reloading = False

    # Refresh ui because of async running
    Common.ui_refresh()


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
    # pcoll.load('TRANSLATE', os.path.join(icons_other_dir, 'translate.png'), 'IMAGE')

    preview_collections['custom_icons'] = pcoll


def unload_icons():
    print('UNLOADING ICONS!')
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    print('DONE!')


def check_for_update_background(force_update=False):
    global reloading, auto_updated
    if reloading:
        return

    if not force_update:
        if auto_updated:
            return
        auto_updated = True

    reloading = True

    thread = Thread(target=check_for_update, args=[force_update])
    thread.start()


def check_for_update(force_update):
    if force_update:
        print('Force updating supporter list..')
        download_file()
    elif update_needed():
        print('Updating supporter list..')
        download_file()
    else:
        finish_reloading()


def update_needed():
    # print('CHECK UPDATE')
    try:
        with urllib.request.urlopen("https://api.github.com/repos/Darkblader24/cats_supporter_list/commits/master") as url:
            data = json.loads(url.read().decode())
    except urllib.error.URLError:
        print('URL ERROR')
        return False

    try:
        last_commit_date = datetime.strptime(data['commit']['author']['date'], globs.time_format_github)
    except KeyError:
        print('DATA NOT READABLE')
        return False

    global last_update
    commit_date_str = last_commit_date.strftime(globs.time_format)
    last_update = commit_date_str
    # print(last_update)

    if not Settings.get_last_supporter_update():
        print('SETTINGS NOT FOUND')
        return True

    last_update_str = Settings.get_last_supporter_update()

    if commit_date_str == last_update_str:
        # print('COMMIT IDENTICAL')
        return False

    utc_now = datetime.strptime(datetime.now(timezone.utc).strftime(globs.time_format), globs.time_format)
    time_delta = abs((utc_now - last_commit_date).total_seconds())

    # print(utc_now)
    # print(time_delta)

    # print('SECONDS SINCE LAST UPDATE:', time_delta)
    if time_delta <= 120:
        print('COMMIT TOO CLOSE')
        return False

    print('UPDATE NEEDED')
    return True
