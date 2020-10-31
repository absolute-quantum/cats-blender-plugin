if "bpy" not in locals():
    # print('STARTUP TOOLS!!')
    import bpy
    from . import register
    from . import armature
    from . import armature_bones
    from . import armature_manual
    from . import armature_custom
    from . import atlas
    from . import bonemerge
    from . import common
    from . import copy_protection
    from . import credits
    from . import decimation
    from . import eyetracking
    from . import fbx_patch
    from . import importer
    from . import material
    from . import rootbone
    from . import bake
    from . import settings
    from . import shapekey
    from . import supporter
    from . import translate
    from . import viseme
else:
    # print('RELOAD TOOLS!!')
    import importlib
    importlib.reload(register)  # Has to be first
    importlib.reload(armature)
    importlib.reload(armature_bones)
    importlib.reload(armature_manual)
    importlib.reload(armature_custom)
    importlib.reload(atlas)
    importlib.reload(bonemerge)
    importlib.reload(common)
    importlib.reload(copy_protection)
    importlib.reload(credits)
    importlib.reload(decimation)
    importlib.reload(eyetracking)
    importlib.reload(fbx_patch)
    importlib.reload(importer)
    importlib.reload(material)
    importlib.reload(rootbone)
    importlib.reload(bake)
    importlib.reload(settings)
    importlib.reload(shapekey)
    importlib.reload(supporter)
    importlib.reload(translate)
    importlib.reload(viseme)
