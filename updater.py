import os
import bpy
import time
import json
import urllib
import shutil
import pathlib
import zipfile
from collections import OrderedDict
from threading import Thread

is_checking_for_update = False

version_list = None
current_version = []
update_needed = False
latest_version = None
latest_version_str = ''
checked_with_button = False
update_finished = False

main_dir = os.path.dirname(__file__)
downloads_dir = os.path.join(main_dir, "downloads")

# Icons for UI
ICON_URL = 'URL'
if bpy.app.version < (2, 79, 9):
    ICON_URL = 'LOAD_FACTORY'


class CheckForUpdateButton(bpy.types.Operator):
    bl_idname = 'cats_updater.check_for_update'
    bl_label = 'Check now for Update'
    bl_description = 'Checks if a new update is available for CATS'

    @classmethod
    def poll(cls, context):
        return not is_checking_for_update

    def execute(self, context):
        global checked_with_button
        checked_with_button = True
        check_for_update_background()
        return {'FINISHED'}


class UpdateToLatestButton(bpy.types.Operator):
    bl_idname = 'cats_updater.update_latest'
    bl_label = 'Update Now'
    bl_description = 'Updates CATS to the latest version'

    @classmethod
    def poll(cls, context):
        return update_needed

    def execute(self, context):
        update_now(latest=True)
        return {'FINISHED'}


class UpdateToSelectedButton(bpy.types.Operator):
    bl_idname = 'cats_updater.update_selected'
    bl_label = 'Update to Selected version'
    bl_description = 'Updates CATS to the selected version'

    @classmethod
    def poll(cls, context):
        if is_checking_for_update or not version_list:
            return False
        return True

    def execute(self, context):
        update_now(version=context.scene.cats_updater_version_list)
        return {'FINISHED'}


class UpdateToDevButton(bpy.types.Operator):
    bl_idname = 'cats_updater.update_dev'
    bl_label = 'Update to Development version'
    bl_description = 'Updates CATS to the Development version'

    def execute(self, context):
        update_now(dev=True)
        return {'FINISHED'}


class ShowPatchnotesPanel(bpy.types.Operator):
    bl_idname = 'cats_updater.show_patchnotes'
    bl_label = 'Patchnotes'
    bl_description = 'Shows the patchnotes of the selected version'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 11.5, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'cats_updater_version_list')

        if context.scene.cats_updater_version_list:
            version = version_list.get(context.scene.cats_updater_version_list)

            col.separator()
            row = col.row(align=True)
            row.label(text='Released: ' + version[2])

            col.separator()
            for line in version[1].replace('**', '').split('\r\n'):
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=line)

        col.separator()


def check_for_update_background():
    global is_checking_for_update
    if is_checking_for_update:
        print('UPDATE CHECK ALREADY IN PROGRESS')
        return
    is_checking_for_update = True

    thread = Thread(target=check_for_update, args=[])
    thread.start()


def check_for_update():
    print('START UPDATE CHECK')

    # Get all releases from Github
    get_github_tags()

    # Check if an update is needed
    global update_needed
    update_needed = check_for_update_available()
    if not update_needed:
        print('NO UPDATE NEEDED')
    else:
        print('UPDATE NEEDED')

    finish_update_checking()


def get_github_tags():
    print('GET RELEASES')
    global version_list
    try:
        with urllib.request.urlopen("https://api.github.com/repos/michaeldegroot/cats-blender-plugin/releases") as url:
            data = json.loads(url.read().decode())
    except urllib.error.URLError:
        print('URL ERROR')
        return False

    version_list = OrderedDict()
    for version in data:
        if 'yanked' in version.get('name').lower():
            continue
        version_list[version.get('tag_name')] = [version.get('zipball_url'), version.get('body'), version.get('published_at').split('T')[0]]

    for version, info in version_list.items():
        print(version, info[0], info[2])


def check_for_update_available():
    if not version_list:
        return False

    global latest_version, latest_version_str
    latest_version = []
    for version in version_list.keys():
        latest_version_str = version
        for i in version.split('.'):
            if i.isdigit():
                latest_version.append(int(i))
        break

    print(latest_version, '>', current_version)
    if latest_version > current_version:
        return True


def finish_update_checking():
    global is_checking_for_update
    is_checking_for_update = False
    ui_refresh()


def ui_refresh():
    # A way to refresh the ui
    refreshed = False
    while not refreshed:
        if hasattr(bpy.data, 'window_managers'):
            for windowManager in bpy.data.window_managers:
                for window in windowManager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
            refreshed = True
            # print('Refreshed UI')
        else:
            time.sleep(0.5)


def update_now(version=None, latest=False, dev=False):
    if dev:
        print('UPDATE TO DEVELOPMENT')
        update_link = 'https://github.com/michaeldegroot/cats-blender-plugin/archive/development.zip'
    elif latest or not version:
        print('UPDATE TO ' + latest_version_str)
        update_link = version_list.get(latest_version_str)[0]
    else:
        print('UPDATE TO ' + version)
        update_link = version_list[version][0]

    download_file(update_link)


def download_file(update_url):
    # Load all the directories and files
    update_zip_file = os.path.join(downloads_dir, "cats-update.zip")

    # Remove existing download folder
    if os.path.isdir(downloads_dir):
        print("DOWNLOAD FOLDER EXISTED")
        shutil.rmtree(downloads_dir)

    # Create download folder
    pathlib.Path(downloads_dir).mkdir(exist_ok=True)

    # Download zip
    print('DOWNLOAD FILE')
    try:
        urllib.request.urlretrieve(update_url, update_zip_file)
    except urllib.error.URLError:
        print("FILE COULD NOT BE DOWNLOADED")
        shutil.rmtree(downloads_dir)
        # finish_reloading()
        return
    print('DOWNLOAD FINISHED')

    # If zip is not downloaded, abort
    if not os.path.isfile(update_zip_file):
        print("ZIP NOT FOUND!")
        shutil.rmtree(downloads_dir)
        # finish_reloading()
        return

    # Extract the downloaded zip
    print('EXTRACTING ZIP')
    with zipfile.ZipFile(update_zip_file, "r") as zip_ref:
        zip_ref.extractall(downloads_dir)
    print('EXTRACTED')

    # Delete the extracted zip file
    print('REMOVING ZIP FILE')
    os.remove(update_zip_file)

    # Detect the extracted folders and files
    print('SEARCHING FOR INIT 1')

    def searchInit(path):
        print('SEARCHING IN ' + path)
        files = os.listdir(path)
        if "__init__.py" in files:
            print('FOUND')
            return path
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        if len(folders) != 1:
            print(len(folders), 'FOLDERS DETECTED')
            return None
        print('GOING DEEPER')
        return searchInit(os.path.join(path, folders[0]))

    print('SEARCHING FOR INIT 2')
    extracted_zip_dir = searchInit(downloads_dir)
    if not extracted_zip_dir:
        print("INIT NOT FOUND!")
        shutil.rmtree(downloads_dir)
        # finish_reloading()
        return

    # Remove old addon files
    clean_addon_dir()

    # Move the extracted files to their correct places
    def move_files(from_dir, to_dir):
        print('MOVE FILES TO DIR:', to_dir)
        files = os.listdir(from_dir)
        for file in files:
            file_dir = os.path.join(from_dir, file)
            target_dir = os.path.join(to_dir, file)
            print('MOVE', file_dir)
            
            # If file exists
            if os.path.isfile(file_dir) and os.path.isfile(target_dir):
                os.remove(target_dir)
                shutil.move(file_dir, to_dir)
                print('REMOVED AND MOVED', file)

            elif os.path.isdir(file_dir) and os.path.isdir(target_dir):
                move_files(file_dir, target_dir)

            else:
                shutil.move(file_dir, to_dir)
                print('MOVED', file)

    move_files(extracted_zip_dir, main_dir)

    # Delete download folder
    print('DELETE DOWNLOADS DIR')
    shutil.rmtree(downloads_dir)

    global update_finished
    update_finished = True

    print("UPDATE DONE!")

    # # Save update time in settings
    # tools.settings.set_last_supporter_update(last_update)
    #
    # # Reload supporters
    # reload_supporters()


def clean_addon_dir():
    print("CLEAN ADDON FOLDER")

    # first remove root files and folders (except update folder, important folders and resource folder)
    files = [f for f in os.listdir(main_dir) if os.path.isfile(os.path.join(main_dir, f))]
    folders = [f for f in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, f))]

    for f in files:
        file = os.path.join(main_dir, f)
        try:
            os.remove(file)
            print("Clean removing file {}".format(file))
        except OSError:
            print("Failed to pre-remove file " + file)

    for f in folders:
        folder = os.path.join(main_dir, f)
        if f.startswith('.') or f == 'resources' or f == 'downloads':
            continue

        try:
            shutil.rmtree(folder)
            print("Clean removing folder and contents {}".format(folder))
        except OSError:
            print("Failed to pre-remove folder " + folder)

    # then remove resource files and folders (except settings and google dict)
    resources_folder = os.path.join(main_dir, 'resources')
    files = [f for f in os.listdir(resources_folder) if os.path.isfile(os.path.join(resources_folder, f))]
    folders = [f for f in os.listdir(resources_folder) if os.path.isdir(os.path.join(resources_folder, f))]

    for f in files:
        if f == 'settings.json' or f == 'dictionary_google.json':
            continue
        file = os.path.join(resources_folder, f)
        try:
            os.remove(file)
            print("Clean removing file {}".format(file))
        except OSError:
            print("Failed to pre-remove " + file)

    for f in folders:
        folder = os.path.join(resources_folder, f)
        try:
            shutil.rmtree(folder)
            print("Clean removing folder and contents {}".format(folder))
        except OSError:
            print("Failed to pre-remove folder " + folder)


def get_version_list(self, context):
    choices = []
    if version_list:
        for version in version_list.keys():
            choices.append((version, version, version))

    bpy.types.Object.Enum = choices
    return bpy.types.Object.Enum


def layout_split(layout, factor=0.0, align=False):
    if bpy.app.version < (2, 79, 9):
        return layout.split(percentage=factor, align=align)
    return layout.split(factor=factor, align=align)


def draw_updater_panel(context, layout):
    box = layout.box()
    col = box.column(align=True)

    row = col.row(align=True)
    row.scale_y = 0.8
    row.label(text='Updates:', icon=ICON_URL)
    col.separator()

    if update_finished:
        col.separator()
        row = col.row(align=True)
        row.label(text='Restart Blender to complete update!', icon='ERROR')
        col.separator()
        return

    if is_checking_for_update:
        if not checked_with_button:
            row = col.row(align=True)
            row.scale_y = 1.7
            row.operator(CheckForUpdateButton.bl_idname, text='Checking..')
        else:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.7
            row.operator(CheckForUpdateButton.bl_idname, text='Checking..')
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.7
            row.operator(CheckForUpdateButton.bl_idname, text="", icon='FILE_REFRESH')

    elif update_needed:
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.7
        row.operator(UpdateToLatestButton.bl_idname, text='Update now to ' + latest_version_str)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_y = 1.7
        row.operator(CheckForUpdateButton.bl_idname, text="", icon='FILE_REFRESH')

    elif not checked_with_button or not version_list:
        row = col.row(align=True)
        row.scale_y = 1.7
        row.operator(CheckForUpdateButton.bl_idname, text='Check now for Update')

    else:
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.7
        row.operator(UpdateToLatestButton.bl_idname, text='Up to Date!')
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_y = 1.7
        row.operator(CheckForUpdateButton.bl_idname, text="", icon='FILE_REFRESH')

    col.separator()
    col.separator()
    row = layout_split(col, factor=0.6, align=True)
    row.scale_y = 1
    row.label(text="Select Version:")
    row.prop(context.scene, 'cats_updater_version_list', text='')

    row = layout_split(col, factor=0.6, align=True)
    row.scale_y = 1.4
    row.operator(UpdateToSelectedButton.bl_idname, text='Install Selected Version')
    row.operator(ShowPatchnotesPanel.bl_idname, text='Show Patchnotes')

    col.separator()
    col.separator()
    row = col.row(align=True)
    row.scale_y = 1.4
    row.operator(UpdateToDevButton.bl_idname, text='Install Development Version')


def register(bl_info):
    global current_version

    # Get current version
    current_version = []
    for i in bl_info['version']:
        current_version.append(i)

    bpy.types.Scene.cats_updater_version_list = bpy.props.EnumProperty(
        name='Version',
        description='Select the version you want to install\n',
        items=get_version_list
    )

    # Register all Updater classes
    bpy.utils.register_class(CheckForUpdateButton)
    bpy.utils.register_class(UpdateToLatestButton)
    bpy.utils.register_class(UpdateToSelectedButton)
    bpy.utils.register_class(UpdateToDevButton)
    bpy.utils.register_class(ShowPatchnotesPanel)


def unregister():
    # Unregister all Updater classes
    bpy.utils.unregister_class(CheckForUpdateButton)
    bpy.utils.unregister_class(UpdateToLatestButton)
    bpy.utils.unregister_class(UpdateToSelectedButton)
    bpy.utils.unregister_class(UpdateToDevButton)
    bpy.utils.unregister_class(ShowPatchnotesPanel)

    del bpy.types.Scene.cats_updater_version_list
