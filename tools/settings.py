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
# Edits by: Hotox

import os
import bpy
import json
import copy
import time
import pathlib
import collections
from threading import Thread
from datetime import datetime, timezone
from collections import OrderedDict

from .. import globs
from ..tools.register import register_wrap
# from ..googletrans import Translator  # Todo Remove this
from ..extern_tools.google_trans_new.google_trans_new import google_translator
from . import translate as Translate
from ..translations import t

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
settings_file = os.path.join(resources_dir, "settings.json")

settings_data = None
settings_data_unchanged = None

# Settings name = [Default Value, Require Blender Restart]
settings_default = OrderedDict()
settings_default['show_mmd_tabs'] = [True, False]
settings_default['embed_textures'] = [False, False]
# settings_default['use_custom_mmd_tools'] = [False, True]

lock_settings = False


@register_wrap
class RevertChangesButton(bpy.types.Operator):
    bl_idname = 'cats_settings.revert'
    bl_label = t('RevertChangesButton.label')
    bl_description = t('RevertChangesButton.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for setting in settings_default.keys():
            setattr(bpy.context.scene, setting, settings_data_unchanged.get(setting))
        save_settings()
        self.report({'INFO'}, t('RevertChangesButton.success'))
        return {'FINISHED'}


@register_wrap
class ResetGoogleDictButton(bpy.types.Operator):
    bl_idname = 'cats_settings.reset_google_dict'
    bl_label = t('ResetGoogleDictButton.label')
    bl_description = t('ResetGoogleDictButton.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        Translate.reset_google_dict()
        Translate.load_translations()
        self.report({'INFO'}, t('ResetGoogleDictButton.resetInfo'))
        return {'FINISHED'}


@register_wrap
class DebugTranslations(bpy.types.Operator):
    bl_idname = 'cats_settings.debug_translations'
    bl_label = t('DebugTranslations.label')
    bl_description = t('DebugTranslations.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.context.scene.debug_translations = True
        translator = google_translator()
        try:
            translator.translate('猫')
        except:
            self.report({'INFO'}, t('DebugTranslations.error'))

        bpy.context.scene.debug_translations = False
        self.report({'INFO'}, t('DebugTranslations.success'))
        return {'FINISHED'}


def load_settings():
    # print('READING SETTINGS FILE')
    global settings_data, settings_data_unchanged

    # Load settings file and reset it if errors are found
    try:
        with open(settings_file, encoding="utf8") as file:
            settings_data = json.load(file, object_pairs_hook=collections.OrderedDict)
            # print('SETTINGS LOADED!')
    except FileNotFoundError:
        print("SETTINGS FILE NOT FOUND!")
        reset_settings(full_reset=True)
        return
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN SETTINGS FILE")
        reset_settings(full_reset=True)
        return

    if not settings_data:
        print("NO DATA IN SETTINGS FILE")
        reset_settings(full_reset=True)
        return

    to_reset_settings = []

    # Check for missing entries, reset if necessary
    for setting in ['last_supporter_update']:
        if setting not in settings_data and setting not in to_reset_settings:
            to_reset_settings.append(setting)
            print('RESET SETTING', setting)

    # Check for other missing entries, reset if necessary
    for setting in settings_default.keys():
        if setting not in settings_data and setting not in to_reset_settings:
            to_reset_settings.append(setting)
            print('RESET SETTING', setting)

    # Check if timestamps are correct
    utc_now = datetime.strptime(datetime.now(timezone.utc).strftime(globs.time_format), globs.time_format)
    for setting in ['last_supporter_update']:
        if setting not in to_reset_settings and settings_data.get(setting):
            try:
                timestamp = datetime.strptime(settings_data.get(setting), globs.time_format)
            except ValueError:
                to_reset_settings.append(setting)
                print('RESET TIME', setting)
                continue

            # If timestamp is in future
            time_delta = (utc_now - timestamp).total_seconds()
            if time_delta < 0:
                to_reset_settings.append(setting)
                print('TIME', setting, 'IN FUTURE!', time_delta)
            else:
                pass
                # print('TIME', setting, 'IN PAST!', time_delta)

    # If there are settings to reset, reset them
    if to_reset_settings:
        reset_settings(to_reset_settings=to_reset_settings)
        return

    # Save the settings into the unchanged settings in order to know if the settings changed later
    settings_data_unchanged = copy.deepcopy(settings_data)


def save_settings():
    with open(settings_file, 'w', encoding="utf8") as outfile:
        json.dump(settings_data, outfile, ensure_ascii=False, indent=4)


def reset_settings(full_reset=False, to_reset_settings=None):
    if not to_reset_settings:
        full_reset = True

    global settings_data, settings_data_unchanged

    if full_reset:
        settings_data = OrderedDict()
        settings_data['last_supporter_update'] = None

        for setting, value in settings_default.items():
            settings_data[setting] = value[0]

    else:
        for setting in to_reset_settings:
            if setting in settings_default.keys():
                settings_data[setting] = settings_default[setting][0]
            else:
                settings_data[setting] = None

    save_settings()

    settings_data_unchanged = copy.deepcopy(settings_data)
    print('SETTINGS RESET')


def start_apply_settings_timer():
    global lock_settings
    lock_settings = True
    thread = Thread(target=apply_settings, args=[])
    thread.start()


def apply_settings():
    applied = False
    while not applied:
        if hasattr(bpy.context, 'scene'):
            try:
                for setting in settings_default.keys():
                    setattr(bpy.context.scene, setting, settings_data.get(setting))
            except AttributeError:
                time.sleep(0.3)
                continue

            applied = True
            # print('Refreshed Settings!')
        else:
            time.sleep(0.3)

    # Unlock settings
    global lock_settings
    lock_settings = False


def settings_changed():
    for setting, value in settings_default.items():
        if value[1] and settings_data.get(setting) != settings_data_unchanged.get(setting):
            return True
    return False


def update_settings(self, context):
    if lock_settings:
        return
    for setting in settings_default.keys():
        settings_data[setting] = getattr(bpy.context.scene, setting)
    save_settings()


def set_last_supporter_update(last_supporter_update):
    settings_data['last_supporter_update'] = last_supporter_update
    save_settings()


def get_last_supporter_update():
    return settings_data.get('last_supporter_update')


def get_use_custom_mmd_tools():
    return settings_data.get('use_custom_mmd_tools')


def get_embed_textures():
    return settings_data.get('embed_textures')
