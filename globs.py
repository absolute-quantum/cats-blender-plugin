import bpy
import copy

# for bone root parenting
root_bones = {}
root_bones_choices = {}

# Keeps track of operations done for unit testing
testing = []

dev_branch = False
dict_found = False
version = None
version_str = ''
is_reloading = False

package = 'cats'

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

# List all the supporters here
supporters = [
    # ['Display name', 'Icon name', 'Start Date', Support Tier]  yyyy-mm-dd  The start date should be the date when the update goes live to ensure 30 days
    ['Xeverian', 'xeverian', '2017-12-19', 0],  # 45
    ['Tupper', 'tupper', '2017-12-19', 1],  # 50
    # ['Jazneo', 'jazneo', '2017-12-19', 0],
    ['idea', 'idea', '2017-12-19', 0],  # -patr
    ['RadaruS', 'radaruS', '2017-12-19', 0],  # emtpy pic
    # ['Kry10', 'kry10', '2017-12-19', 0],
    # ['Smead', 'smead', '2017-12-25', 0],
    # ['kohai.istool', 'kohai.istool', '2017-12-25', 0],
    ['Str4fe', 'str4fe', '2017-12-25', 0],  # -niem
    ["Ainrehtea Dal'Nalirtu", "Ainrehtea Dal'Nalirtu", '2017-12-25', 0],
    # ['Wintermute', 'wintermute', '2017-12-19', 0],
    ['Raikin', 'raikin', '2017-12-25', 0],  # -soni
    ['BerserkerBoreas', 'berserkerboreas', '2017-12-25', 0],
    ['ihatemondays', 'ihatemondays', '2017-12-25', 0],
    ['Derpmare', 'derpmare', '2017-12-25', 0],
    # ['Bin Chicken', 'bin_chicken', '2017-12-25', 0],
    ['Chikan Celeryman', 'chikan_celeryman', '2017-12-25', 0],
    # ['migero', 'migero', '2018-01-05', 0],
    ['Ashe', 'ashe', '2018-01-05', 0],  # 50
    ['Quadriple', 'quadriple', '2018-01-05', 0],  # 30
    # ['abrownbag', 'abrownbag', '2018-01-05', 1],
    ['Azuth', 'Azuth', '2018-01-05', 0],
    ['goblox', 'goblox', '2018-01-05', 1],
    # ['Rikku', 'Rikku', '2018-01-05', 0],
    # ['azupwn', 'azupwn', '2018-01-05', 0],
    ['m o t h', 'm o t h', '2018-01-05', 0],
    # ['Yorx', 'Yorx', '2018-01-05', 0],
    # ['Buffy', 'Buffy', '2018-01-05', 0],
    ['Tomnautical', 'Tomnautical', '2018-01-05', 0],  # -psyo
    # ['akarinjelly', 'Jelly', '2018-01-05', 0],
    ['Atirion', 'Atirion', '2018-01-05', 0],
    ['Lydania', 'Lydania', '2018-01-05', 0],  # -tobi
    ['Shanie', 'Shanie-senpai', '2018-01-05', 0],  # -shan
    # ['Kal [Thramis]', 'Kal', '2018-01-12', 0],
    ['Sifu', 'Sifu', '2018-01-12', 0],  # -ylon
    # ['Lil Clone', 'Lil Clone', '2018-01-12', 0],
    ['Naranar', 'Naranar', '2018-01-12', 1],
    # ['gwigz', 'gwigz', '2018-01-12', 0],
    # ['Lux', 'Lux', '2018-01-12', 0],
    ['liquid (retso)', 'liquid', '2018-01-12', 0],  # -oste
    # ['GreenTeaGamer', 'GreenTeaGamer', '2018-01-12', 0],
    # ['Desruko', 'Desruko', '2018-01-12', 0],
    ['Mute_', 'Mute_', '2018-01-12', 0],
    # icewind (don't add)
    ['qy_li', 'qy_li', '2018-01-22', 1],  # emtpy pic  - lqy
    # ['Sixnalia', 'Sixnalia', '2018-01-22', 0],
    ['ReOL', 'ReOL', '2018-01-22', 0],  # emtpy pic
    ['Rezinion', 'Rezinion', '2018-01-22', 0],
    ['Karma', 'Karma', '2018-01-22', 0],
    # ['\1B', 'BOXMOB', '2018-01-22', 0],
    # ['\2O', 'BOXMOB', '2018-01-22', 0],
    # ['\3X', 'BOXMOB', '2018-01-22', 0],
    # ['\1M', 'BOXMOB', '2018-01-22', 0],
    # ['\2O', 'BOXMOB', '2018-01-22', 0],
    # ['\3B', 'BOXMOB', '2018-01-22', 0],
    ['SolarSnowball', 'SolarSnowball', '2018-01-22', 0],  # is later in form list
    # ['Hordaland', 'Hordaland', '2018-01-22', 0],
    ['Bones', 'Bones', '2018-01-22', 0],  # PP 50
    # Joshua (onodaTV)    # cancelled april, don't add
    # charlie (discord) 24th missing
    ['Axo_', 'Axo_', '2018-04-10', 0],
    # Jerry (jt1990)
    ['Dogniss', 'Dogniss', '2018-03-10', 0],  # -Forc
    ['Syntion', 'Syntion', '2018-05-13', 0],  # -fabi
    ['Sheet_no_mana', 'Sheet_no_mana', '2018-04-10', 0],  # emtpy pic  -fina
    # Marcus (m.johannson) (ignore)
    ['Awrini', 'Awrini', '2018-03-10', 0],
    # ['Smooth', 'Smooth', '2018-03-10', 0],
    # FlammaRilva (fls81245) (ignore)
    ['NekoNatsuki', 'NekoNatsuki', '2018-03-10', 0],  # 42
    # Checked until here

    ['AlphaSatanOmega', 'AlphaSatanOmega', '2018-03-10', 0],
    # Murakuumoo (murakuumoo)
    ['Curio', 'Curio', '2018-03-10', 1],
    ['Deathofirish', 'Deathofirish', '2018-04-17', 0],  # emtpy pic  -jaco
    # eduardo (botello.eduardo19)
    ['Runda', 'Runda', '2018-04-17', 0],
    ['Rurikaze', 'Rurikaze', '2018-05-09', 0],  # -mist
    ['Brindin_wF', 'Brindin_wF', '2018-04-17', 0],  # -Bran
    ['Serry Jane', 'Serry_Jane', '2018-04-17', 1],  # emtpy pic  -ianc
    ['GV-97', 'GV-97', '2018-05-09', 0],  # -niels
    ['COMMEN', 'COMMEN', '2018-05-09', 0],  # emtpy pic  -do20
    ['Antivirus-Chan', 'Antivirus-Chan', '2018-05-09', 0],  #  -frost
    ['Rayduxz', 'Rayduxz', '2018-05-09', 0],  #  -hats
    ['BemVR', 'BemVR', '2018-05-14', 0],  #  -bemv
    # PorcelainShrine (questzero)
]