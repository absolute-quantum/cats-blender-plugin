"""Blender 5.2 compatibility smoke tests for the maintained CATS fork."""

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy


repo_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_dir.parent))
addon = importlib.import_module(repo_dir.name)


def create_mesh_object():
    mesh = bpy.data.meshes.new("CATS_Smoke_Mesh")
    mesh.from_pydata(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
        [],
        [(0, 1, 2)],
    )
    obj = bpy.data.objects.new("CATS_Smoke_Mesh", mesh)
    bpy.context.collection.objects.link(obj)
    material = bpy.data.materials.new("CATS_Smoke_Material")
    material.use_nodes = True
    mesh.materials.append(material)
    return obj


def create_armature_object():
    armature = bpy.data.armatures.new("CATS_Smoke_Armature")
    obj = bpy.data.objects.new("CATS_Smoke_Armature", armature)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bone = armature.edit_bones.new("Bone")
    bone.head = (0.0, 0.0, 0.0)
    bone.tail = (0.0, 0.0, 1.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def run():
    addon.register()

    # Settings are applied on Blender's main thread and must not spawn a
    # background bpy.context access.
    result = addon.tools.settings.apply_settings()
    assert result is None

    mesh_obj = create_mesh_object()
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    # Principled BSDF input names changed to "Emission Color".
    result = bpy.ops.cats_bake.preset_desktop()
    assert result == {'FINISHED'}
    assert hasattr(bpy.context.scene, "bake_pass_emit")

    # Vertex colors are color attributes in current Blender.
    color_attributes = mesh_obj.data.color_attributes
    color = color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
    color_attributes.active_color = color
    assert color_attributes.active_color == color

    # Node group sockets use NodeTree.interface in Blender 4+.
    from mmd_tools_local.core.shader import _MaterialMorph
    shader = _MaterialMorph._MaterialMorph__get_shader("Add")
    assert shader.interface.items_tree
    assert any(item.name == "Ambient1" for item in shader.interface.items_tree)

    # MMD display frames map to bone collections after bone groups removal.
    from mmd_tools_local.operators.display_item import DisplayItemQuickSetup
    armature_obj = create_armature_object()
    bpy.context.scene.armature = armature_obj.name
    mesh_obj.parent = armature_obj
    mesh_obj.shape_key_add(name="Basis")
    mesh_obj.shape_key_add(name="Smile")

    # Regression for the native IDProperty use-after-free that originally
    # crashed Blender while joining meshes.
    armature_obj["CUSTOM"] = {"unrelated": 1}
    addon.tools.common.save_shapekey_order(mesh_obj.name)
    addon.tools.common.repair_shapekey_order(mesh_obj.name)
    assert list(armature_obj["CUSTOM"]["shape_key_order"]) == ["Basis", "Smile"]

    frame = SimpleNamespace(
        name="Main",
        data=[SimpleNamespace(type='BONE', name="Bone")],
    )
    mmd_root = SimpleNamespace(display_item_frames=[frame])
    DisplayItemQuickSetup.apply_bone_groups(mmd_root, armature_obj)
    collection = armature_obj.data.collections.get("Main")
    assert collection is not None
    assert "Bone" in collection.bones

    addon.unregister()
    print("CATS_BLENDER52_SMOKE_OK")


if __name__ == "__main__":
    run()
