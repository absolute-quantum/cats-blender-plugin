import globs

if not globs.is_reloading:
    # print('STARTUP TOOLS!!')
    import tools.register
    import tools.armature
    import tools.armature_bones
    import tools.armature_manual
    import tools.armature_custom
    import tools.atlas
    import tools.bonemerge
    import tools.common
    import tools.copy_protection
    import tools.credits
    import tools.decimation
    import tools.eyetracking
    import tools.importer
    import tools.material
    import tools.rootbone
    import tools.settings
    import tools.shapekey
    import tools.supporter
    import tools.translate
    import tools.viseme
else:
    # print('RELOAD TOOLS!!')
    import importlib
    importlib.reload(tools.register)  # Has to be first
    importlib.reload(tools.armature)
    importlib.reload(tools.armature_bones)
    importlib.reload(tools.armature_manual)
    importlib.reload(tools.armature_custom)
    importlib.reload(tools.atlas)
    importlib.reload(tools.bonemerge)
    importlib.reload(tools.common)
    importlib.reload(tools.copy_protection)
    importlib.reload(tools.credits)
    importlib.reload(tools.decimation)
    importlib.reload(tools.eyetracking)
    importlib.reload(tools.importer)
    importlib.reload(tools.material)
    importlib.reload(tools.rootbone)
    importlib.reload(tools.settings)
    importlib.reload(tools.shapekey)
    importlib.reload(tools.supporter)
    importlib.reload(tools.translate)
    importlib.reload(tools.viseme)
