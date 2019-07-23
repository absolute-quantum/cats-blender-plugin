import bpy

# for bone root parenting
root_bones = {}
root_bones_choices = {}

# Keeps track of operations done for unit testing
testing = []

dev_branch = False
dict_found = False
version = None
version_str = ''

# other
time_format = "%Y-%m-%d %H:%M:%S"
time_format_github = "%Y-%m-%dT%H:%M:%SZ"

# Icons for UI
ICON_ADD, ICON_REMOVE = 'ADD', 'REMOVE'
ICON_URL = 'URL'
ICON_SETTINGS = 'SETTINGS'
ICON_ALL = 'PROP_ON'
ICON_MOD_ARMATURE = 'MOD_ARMATURE'
ICON_FIX_MODEL = 'SHADERFX'
ICON_EYE_ROTATION = 'DRIVER_ROTATIONAL_DIFFERENCE'
ICON_POSE_MODE = 'POSE_HLT'
ICON_SHADING_TEXTURE = 'SHADING_TEXTURE'
ICON_PROTECT = 'LOCKED'
ICON_UNPROTECT = 'UNLOCKED'
ICON_EXPORT = 'EXPORT'
if bpy.app.version < (2, 79, 9):
    ICON_ADD, ICON_REMOVE = 'ZOOMIN', 'ZOOMOUT'
    ICON_URL = 'LOAD_FACTORY'
    ICON_SETTINGS = 'SCRIPTPLUGINS'
    ICON_ALL = 'META_BALL'
    ICON_MOD_ARMATURE = 'OUTLINER_OB_ARMATURE'
    ICON_FIX_MODEL = 'BONE_DATA'
    ICON_EYE_ROTATION = 'MAN_ROT'
    ICON_POSE_MODE = 'POSE_DATA'
    ICON_SHADING_TEXTURE = 'TEXTURE_SHADED'
    ICON_PROTECT = 'KEY_HLT'
    ICON_UNPROTECT = 'KEY_DEHLT'
    ICON_EXPORT = 'LOAD_FACTORY'
