# -*- coding: utf-8 -*-

if "bpy" in locals():
    if bpy.app.version < (2, 71, 0):
        import imp as importlib
    else:
        import importlib
    importlib.reload(prop_bone)
    importlib.reload(prop_camera)
    importlib.reload(prop_lamp)
    importlib.reload(prop_material)
    importlib.reload(prop_object)
    importlib.reload(tool)
    importlib.reload(util_tools)
    importlib.reload(view_prop)
    importlib.reload(view_header)
else:
    import bpy
    from . import (
        prop_bone,
        prop_camera,
        prop_lamp,
        prop_material,
        prop_object,
        tool,
        util_tools,
        view_prop,
        view_header
        )

