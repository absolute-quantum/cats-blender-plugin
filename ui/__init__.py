# GPL License

if "bpy" not in locals():
    # print('STARTUP UI!!')
    import bpy
    from . import main
    from . import armature
    from . import manual
    from . import custom
    from . import decimation
    from . import visemes
    from . import bone_root
    from . import optimization
    from . import scale
    from . import eye_tracking
    from . import copy_protection
    from . import settings_updates
    from . import supporter
    from . import credits
else:
    # print('RELOAD UI!!')
    import importlib
    importlib.reload(main)
    importlib.reload(armature)
    importlib.reload(manual)
    importlib.reload(custom)
    importlib.reload(decimation)
    importlib.reload(visemes)
    importlib.reload(bone_root)
    importlib.reload(optimization)
    importlib.reload(scale)
    importlib.reload(eye_tracking)
    importlib.reload(copy_protection)
    importlib.reload(settings_updates)
    importlib.reload(supporter)
    importlib.reload(credits)
