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
import tools.supporter
from threading import Thread
from datetime import datetime
from collections import OrderedDict

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
settings_file = os.path.join(resources_dir, "settings.json")

settings_data = None
settings_data_unchanged = None


def load_settings():
    print('READING SETTINGS FILE')
    global settings_data, settings_data_unchanged

    # Load settings file and reset it if errors are found
    try:
        with open(settings_file, encoding="utf8") as file:
            settings_data = json.load(file, object_pairs_hook=collections.OrderedDict)
            print('SETTINGS LOADED!')
    except FileNotFoundError:
        print("SETTINGS FILE NOT FOUND!")
        reset_settings()
        return
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN SETTINGS FILE")
        reset_settings()
        return

    # Check for missing entries, reset if neccessary
    if 'last_supporter_update' not in settings_data or 'use_custom_mmd_tools' not in settings_data:
        reset_settings()
        return

    # Check if timestamps are correct
    if settings_data.get('last_supporter_update'):
        try:
            datetime.strptime(settings_data.get('last_supporter_update'), tools.supporter.time_format)
        except ValueError:
            settings_data['last_supporter_update'] = None
            print('RESET TIME')

    # Save the settings into the unchanged settings in order to know if the settings changed later
    settings_data_unchanged = copy.deepcopy(settings_data)


def save_settings():
    with open(settings_file, 'w', encoding="utf8") as outfile:
        json.dump(settings_data, outfile, ensure_ascii=False, indent=4)


def reset_settings():
    global settings_data, settings_data_unchanged
    settings_data = OrderedDict()

    settings_data['last_supporter_update'] = None
    settings_data['use_custom_mmd_tools'] = False

    save_settings()

    settings_data_unchanged = copy.deepcopy(settings_data)
    print('SETTINGS RESET')


def start_apply_settings_timer():
    thread = Thread(target=apply_settings, args=[])
    thread.start()


def apply_settings():
    time.sleep(2)
    bpy.context.scene.use_custom_mmd_tools = settings_data.get('use_custom_mmd_tools')


def settings_changed():
    if settings_data.get('use_custom_mmd_tools') != settings_data_unchanged.get('use_custom_mmd_tools'):
        return True
    return False


def set_last_supporter_update(last_supporter_update):
    settings_data['last_supporter_update'] = last_supporter_update
    save_settings()


def get_last_supporter_update():
    return settings_data.get('last_supporter_update')


def set_use_custom_mmd_tools(self, context):
    settings_data['use_custom_mmd_tools'] = bpy.context.scene.use_custom_mmd_tools
    save_settings()


def use_custom_mmd_tools(self, context):
    return settings_data.get('use_custom_mmd_tools')
