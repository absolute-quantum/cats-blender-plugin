# -*- coding: utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####

# This file is copied from
#   https://github.com/nutti/Screencast-Keys/blob/a16f6c7dd697f6ec7bced5811db4a8144514d320/src/screencast_keys/utils/addon_updater.py


import datetime
import json
import os
import shutil
import ssl
import urllib
import urllib.request
import zipfile
from threading import Lock

import bpy


def get_separator():
    if os.name == "nt":
        return "\\"
    return "/"


def _request(url, json_decode=True):
    # pylint: disable=W0212
    ssl._create_default_https_context = ssl._create_unverified_context
    req = urllib.request.Request(url)

    try:
        result = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP error ({})".format(str(e.code)))
    except urllib.error.URLError as e:
        raise RuntimeError("URL error ({})".format(str(e.reason)))

    data = result.read()
    result.close()

    if json_decode:
        try:
            return json.JSONDecoder().decode(data.decode())
        except Exception as e:
            raise RuntimeError("API response has invalid JSON format ({})"
                               .format(str(e)))

    return data.decode()


def _download(url, path):
    try:
        urllib.request.urlretrieve(url, path)
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP error ({})".format(str(e.code)))
    except urllib.error.URLError as e:
        raise RuntimeError("URL error ({})".format(str(e.reason)))


def _make_workspace_path(addon_dir):
    return addon_dir + get_separator() + "addon_updater_workspace"


def _make_workspace(addon_dir):
    dir_path = _make_workspace_path(addon_dir)
    os.mkdir(dir_path)


def _make_temp_addon_path(addon_dir, url):
    filename = url.split("/")[-1]
    filepath = _make_workspace_path(addon_dir) + get_separator() + filename
    return filepath


def _download_addon(addon_dir, url):
    filepath = _make_temp_addon_path(addon_dir, url)
    _download(url, filepath)


def _replace_addon(addon_dir, info, current_addon_path, offset_path=""):
    # remove current add-on
    if os.path.isfile(current_addon_path):
        os.remove(current_addon_path)
    elif os.path.isdir(current_addon_path):
        shutil.rmtree(current_addon_path)

    # replace to the new add-on
    workspace_path = _make_workspace_path(addon_dir)
    tmp_addon_path = _make_temp_addon_path(addon_dir, info.url)
    _, ext = os.path.splitext(tmp_addon_path)
    if ext == ".zip":
        with zipfile.ZipFile(tmp_addon_path) as zf:
            zf.extractall(workspace_path)
        if offset_path != "":
            src = workspace_path + get_separator() + offset_path
            dst = addon_dir
            shutil.move(src, dst)
    elif ext == ".py":
        shutil.move(tmp_addon_path, addon_dir)
    else:
        raise RuntimeError("Unsupported file extension. (ext: {})".format(ext))


def _get_all_releases_data(owner, repository):
    url = "https://api.github.com/repos/{}/{}/releases".format(owner, repository)
    data = _request(url)

    return data


def _get_all_branches_data(owner, repository):
    url = "https://api.github.com/repos/{}/{}/branches".format(owner, repository)
    data = _request(url)

    return data


def _parse_release_version(version):
    return [int(c) for c in version[1:].split(".")]


# ver1 > ver2   : >  0
# ver1 == ver2  : == 0
# ver1 < ver2   : <  0
def _compare_version(ver1, ver2):
    if len(ver1) < len(ver2):
        ver1.extend([-1 for _ in range(len(ver2) - len(ver1))])
    elif len(ver1) > len(ver2):
        ver2.extend([-1 for _ in range(len(ver1) - len(ver2))])

    def comp(v1, v2, idx):
        if len(v1) == idx:
            return 0        # v1 == v2

        if v1[idx] > v2[idx]:
            return 1        # v1 > v2
        if v1[idx] < v2[idx]:
            return -1       # v1 < v2

        return comp(v1, v2, idx + 1)

    return comp(ver1, ver2, 0)


class AddonUpdaterConfig:
    def __init__(self):
        # Name of owner
        self.owner = ""

        # Name of repository
        self.repository = ""

        # Additional branch for update candidate
        self.branches = []

        # Set minimum release version for update candidate.
        #   e.g. (5, 2) if your release tag name is "v5.2"
        # If you specify (-1, -1), ignore versions less than current add-on
        # version specified in bl_info.
        self.min_release_version = (-1, -1)

        # Target add-on path
        # {"branch/tag": "add-on path"}
        self.target_addon_path = {}

        # Default target add-on path.
        # Search this path if branch/tag is not found in
        # self.target_addon_path.
        self.default_target_addon_path = ""

        # Current add-on path
        self.current_addon_path = ""

        # Blender add-on directory
        self.addon_directory = ""


class UpdateCandidateInfo:
    def __init__(self):
        self.name = ""
        self.url = ""
        self.group = ""   # BRANCH|RELEASE


class AddonUpdaterManager:
    __inst = None
    __lock = Lock()

    __initialized = False
    __bl_info = None
    __config = None
    __update_candidate = []
    __candidate_checked = False
    __error = ""
    __info = ""
    __updated = False

    def __init__(self):
        raise NotImplementedError("Not allowed to call constructor")

    @classmethod
    def __internal_new(cls):
        return super().__new__(cls)

    @classmethod
    def get_instance(cls):
        if not cls.__inst:
            with cls.__lock:
                if not cls.__inst:
                    cls.__inst = cls.__internal_new()

        return cls.__inst

    def init(self, bl_info, config):
        self.__bl_info = bl_info
        self.__config = config
        self.__update_candidate = []
        self.__candidate_checked = False
        self.__error = ""
        self.__info = ""
        self.__updated = False
        self.__initialized = True

    def initialized(self):
        return self.__initialized

    def candidate_checked(self):
        return self.__candidate_checked

    def check_update_candidate(self):
        if not self.initialized():
            raise RuntimeError("AddonUpdaterManager must be initialized")

        self.__update_candidate = []
        self.__candidate_checked = False

        try:
            # setup branch information
            branches = _get_all_branches_data(self.__config.owner,
                                              self.__config.repository)
            for b in branches:
                if b["name"] in self.__config.branches:
                    info = UpdateCandidateInfo()
                    info.name = b["name"]
                    info.url = "https://github.com/{}/{}/archive/{}.zip".format(self.__config.owner, self.__config.repository, b["name"])
                    info.group = 'BRANCH'
                    self.__update_candidate.append(info)

            # setup release information
            releases = _get_all_releases_data(self.__config.owner,
                                              self.__config.repository)
            for r in releases:
                if _compare_version(_parse_release_version(r["tag_name"]),
                                    self.__config.min_release_version) > 0:
                    info = UpdateCandidateInfo()
                    info.name = r["tag_name"]
                    info.url = r["assets"][0]["browser_download_url"]
                    info.group = 'RELEASE'
                    self.__update_candidate.append(info)
        except RuntimeError as e:
            self.__error = bpy.app.translations.pgettext_iface("Failed to check update {}. ({})").format(str(e), datetime.datetime.now())

        self.__info = bpy.app.translations.pgettext_iface("Checked update. ({})").format(datetime.datetime.now())

        self.__candidate_checked = True

    def has_error(self):
        return self.__error != ""

    def error(self):
        return self.__error

    def has_info(self):
        return self.__info != ""

    def info(self):
        return self.__info

    def update(self, version_name):
        if not self.initialized():
            raise RuntimeError("AddonUpdaterManager must be initialized.")

        if not self.candidate_checked():
            raise RuntimeError("Update candidate is not checked.")

        info = None
        for info in self.__update_candidate:
            if info.name == version_name:
                break
        else:
            raise RuntimeError("{} is not found in update candidate"
                               .format(version_name))

        if info is None:
            raise RuntimeError("Not found any update candidates")

        try:
            # create workspace
            _make_workspace(self.__config.addon_directory)
            # download add-on
            _download_addon(self.__config.addon_directory, info.url)

            # get add-on path
            if info.name in self.__config.target_addon_path:
                addon_path = self.__config.target_addon_path[info.name]
            else:
                addon_path = self.__config.default_target_addon_path

            # replace add-on
            offset_path = ""
            if info.group == 'BRANCH':
                offset_path = "{}-{}{}{}".format(
                    self.__config.repository, info.name, get_separator(),
                    addon_path)
            elif info.group == 'RELEASE':
                offset_path = addon_path
            _replace_addon(self.__config.addon_directory,
                           info, self.__config.current_addon_path,
                           offset_path)

            self.__updated = True
            self.__info = bpy.app.translations.pgettext_iface("Updated to {}. ({})").format(info.name, datetime.datetime.now())
        except RuntimeError as e:
            self.__error = bpy.app.translations.pgettext_iface("Failed to update {}. ({})").format(str(e), datetime.datetime.now())

        shutil.rmtree(_make_workspace_path(self.__config.addon_directory))

    def get_candidate_branch_names(self):
        if not self.initialized():
            raise RuntimeError("AddonUpdaterManager must be initialized.")

        if not self.candidate_checked():
            raise RuntimeError("Update candidate is not checked.")

        return [info.name for info in self.__update_candidate]

    def latest_version(self):
        release_versions = [info.name
                            for info in self.__update_candidate
                            if info.group == 'RELEASE']

        latest = ""
        for version in release_versions:
            if latest == "":
                latest = version
            elif _compare_version(_parse_release_version(version),
                                  _parse_release_version(latest)) > 0:
                latest = version

        return latest

    def update_ready(self):
        latest_version = self.latest_version()
        if latest_version == "":
            return False
        compare = _compare_version(_parse_release_version(latest_version), self.__bl_info['version'])
        return compare > 0

    def updated(self):
        return self.__updated



class CheckAddonUpdate(bpy.types.Operator):
    bl_idname = "mmd_tools.check_addon_update"
    bl_label = "Check Update"
    bl_description = "Check Add-on Update"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        updater = AddonUpdaterManager.get_instance()
        updater.check_update_candidate()

        return {'FINISHED'}

class UpdateAddon(bpy.types.Operator):
    bl_idname = "mmd_tools.update_addon"
    bl_label = "Update"
    bl_description = "Update Add-on"
    bl_options = {'INTERNAL'}

    branch_name: bpy.props.StringProperty(
        name="Branch Name",
        description="Branch name to update",
        default="",
    )

    def execute(self, context):
        updater = AddonUpdaterManager.get_instance()
        updater.update(self.branch_name)

        return {'FINISHED'}

def register_updater(bl_info, init_py_file):
    config = AddonUpdaterConfig()
    config.owner = 'UuuNyaa'
    config.repository = 'blender_mmd_tools'
    config.current_addon_path = os.path.dirname(os.path.realpath(init_py_file))
    config.branches = ['main']
    config.addon_directory = os.path.dirname(config.current_addon_path)
    config.min_release_version = (1, 0, 0)
    config.default_target_addon_path = 'mmd_tools'
    config.target_addon_path = {}
    updater = AddonUpdaterManager.get_instance()
    updater.init(bl_info, config)


def unregister_updater():
    pass