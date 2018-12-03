import globs

if not globs.is_reloading:
    # print('STARTUP UI!!')
    import ui.main
    import ui.armature
    import ui.manual
    import ui.custom
    import ui.decimation
    import ui.eye_tracking
    import ui.visemes
    import ui.bone_root
    import ui.optimization
    import ui.copy_protection
    import ui.settings_updates
    import ui.supporter
    import ui.credits
else:
    # print('RELOAD UI!!')
    import importlib
    importlib.reload(ui.main)
    importlib.reload(ui.armature)
    importlib.reload(ui.manual)
    importlib.reload(ui.custom)
    importlib.reload(ui.decimation)
    importlib.reload(ui.eye_tracking)
    importlib.reload(ui.visemes)
    importlib.reload(ui.bone_root)
    importlib.reload(ui.optimization)
    importlib.reload(ui.copy_protection)
    importlib.reload(ui.settings_updates)
    importlib.reload(ui.supporter)
    importlib.reload(ui.credits)