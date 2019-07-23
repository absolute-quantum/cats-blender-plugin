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

# This is directly taken from the export_fbx_bin.py to change it via monkey patching
from . import common as Common


if Common.version_2_79_or_older():
    import bpy
    import time
    import array
    from threading import Thread
    from mathutils import Vector
    from collections import OrderedDict
    from io_scene_fbx import data_types, export_fbx_bin

    from io_scene_fbx.export_fbx_bin import (
        check_skip_material, fbx_mat_properties_from_texture, fbx_template_def_globalsettings, fbx_template_def_null,
        fbx_template_def_bone, fbx_generate_leaf_bones, fbx_template_def_light, fbx_template_def_camera, fbx_animations,
        fbx_template_def_geometry, fbx_template_def_model, fbx_template_def_pose, fbx_template_def_deformer,
        fbx_template_def_material, fbx_template_def_texture_file, fbx_template_def_animstack, fbx_template_def_animlayer,
        fbx_template_def_video, fbx_template_def_animcurvenode, fbx_template_def_animcurve, fbx_skeleton_from_armature
    )
    from io_scene_fbx.fbx_utils import (
        PerfMon, ObjectWrapper, get_blenderID_key, BLENDER_OBJECT_TYPES_MESHLIKE, get_blender_mesh_shape_key,
        BLENDER_OTHER_OBJECT_TYPES, get_blender_empty_key, vcos_transformed_gen, get_blender_mesh_shape_channel_key,
        FBXExportData, get_fbx_uuid_from_key, similar_values_iter
    )


def start_patch_fbx_exporter_timer():
    if Common.version_2_79_or_older():
        thread = Thread(target=time_patch_fbx_exporter, args=[])
        thread.start()


def time_patch_fbx_exporter():
    import time
    found_scene = False
    while not found_scene:
        if hasattr(bpy.context, 'scene'):
            found_scene = True
        else:
            time.sleep(0.5)

    patch_fbx_exporter()


def patch_fbx_exporter():
    if Common.version_2_79_or_older():
        export_fbx_bin.fbx_data_from_scene = fbx_data_from_scene_v279


def fbx_data_from_scene_v279(scene, settings):
    """
    Do some pre-processing over scene's data...
    """
    objtypes = settings.object_types
    dp_objtypes = objtypes - {'ARMATURE'}  # Armatures are not supported as dupli instances currently...
    perfmon = PerfMon()
    perfmon.level_up()

    # ##### Gathering data...

    perfmon.step("FBX export prepare: Wrapping Objects...")

    # This is rather simple for now, maybe we could end generating templates with most-used values
    # instead of default ones?
    objects = OrderedDict()  # Because we do not have any ordered set...
    for ob in settings.context_objects:
        if ob.type not in objtypes:
            continue
        ob_obj = ObjectWrapper(ob)
        objects[ob_obj] = None
        # Duplis...
        ob_obj.dupli_list_create(scene, 'RENDER')
        for dp_obj in ob_obj.dupli_list:
            if dp_obj.type not in dp_objtypes:
                continue
            objects[dp_obj] = None
        ob_obj.dupli_list_clear()

    perfmon.step("FBX export prepare: Wrapping Data (lamps, cameras, empties)...")

    data_lamps = OrderedDict((ob_obj.bdata.data, get_blenderID_key(ob_obj.bdata.data))
                             for ob_obj in objects if ob_obj.type == 'LAMP')
    # Unfortunately, FBX camera data contains object-level data (like position, orientation, etc.)...
    data_cameras = OrderedDict((ob_obj, get_blenderID_key(ob_obj.bdata.data))
                               for ob_obj in objects if ob_obj.type == 'CAMERA')
    # Yep! Contains nothing, but needed!
    data_empties = OrderedDict((ob_obj, get_blender_empty_key(ob_obj.bdata))
                               for ob_obj in objects if ob_obj.type == 'EMPTY')

    perfmon.step("FBX export prepare: Wrapping Meshes...")

    data_meshes = OrderedDict()
    for ob_obj in objects:
        if ob_obj.type not in BLENDER_OBJECT_TYPES_MESHLIKE:
            continue
        ob = ob_obj.bdata
        use_org_data = True
        org_ob_obj = None

        # Do not want to systematically recreate a new mesh for dupliobject instances, kind of break purpose of those.
        if ob_obj.is_dupli:
            org_ob_obj = ObjectWrapper(ob)  # We get the "real" object wrapper from that dupli instance.
            if org_ob_obj in data_meshes:
                data_meshes[ob_obj] = data_meshes[org_ob_obj]
                continue

        is_ob_material = any(ms.link == 'OBJECT' for ms in ob.material_slots)

        if settings.use_mesh_modifiers or ob.type in BLENDER_OTHER_OBJECT_TYPES or is_ob_material:
            # We cannot use default mesh in that case, or material would not be the right ones...
            use_org_data = not (is_ob_material or ob.type in BLENDER_OTHER_OBJECT_TYPES)
            tmp_mods = []
            if use_org_data and ob.type == 'MESH':
                # No need to create a new mesh in this case, if no modifier is active!
                for mod in ob.modifiers:
                    # For meshes, when armature export is enabled, disable Armature modifiers here!
                    if mod.type == 'ARMATURE' and 'ARMATURE' in settings.object_types:
                        tmp_mods.append((mod, mod.show_render))
                        mod.show_render = False
                    if mod.show_render:
                        use_org_data = False
            if not use_org_data:
                tmp_me = ob.to_mesh(scene, apply_modifiers=True,
                                    settings='RENDER' if settings.use_mesh_modifiers_render else 'PREVIEW')
                data_meshes[ob_obj] = (get_blenderID_key(tmp_me), tmp_me, True)
            # Re-enable temporary disabled modifiers.
            for mod, show_render in tmp_mods:
                mod.show_render = show_render
        if use_org_data:
            data_meshes[ob_obj] = (get_blenderID_key(ob.data), ob.data, False)

        # In case "real" source object of that dupli did not yet still existed in data_meshes, create it now!
        if org_ob_obj is not None:
            data_meshes[org_ob_obj] = data_meshes[ob_obj]

    perfmon.step("FBX export prepare: Wrapping ShapeKeys...")

    # ShapeKeys.
    print('Modified Shapekey export by Cats')
    data_deformers_shape = OrderedDict()
    geom_mat_co = settings.global_matrix if settings.bake_space_transform else None
    for me_key, me, _free in data_meshes.values():
        if not (me.shape_keys and len(me.shape_keys.key_blocks) > 1):  # We do not want basis-only relative skeys...
            continue
        if me in data_deformers_shape:
            continue

        shapes_key = get_blender_mesh_shape_key(me)
        # We gather all vcos first, since some skeys may be based on others...
        _cos = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.vertices) * 3
        me.vertices.foreach_get("co", _cos)
        v_cos = tuple(vcos_transformed_gen(_cos, geom_mat_co))
        sk_cos = {}
        for shape in me.shape_keys.key_blocks[1:]:
            shape.data.foreach_get("co", _cos)
            sk_cos[shape] = tuple(vcos_transformed_gen(_cos, geom_mat_co))
        sk_base = me.shape_keys.key_blocks[0]

        for shape in me.shape_keys.key_blocks[1:]:
            # Only write vertices really different from org coordinates!
            shape_verts_co = []
            shape_verts_idx = []

            sv_cos = sk_cos[shape]
            ref_cos = v_cos if shape.relative_key == sk_base else sk_cos[shape.relative_key]
            for idx, (sv_co, ref_co) in enumerate(zip(sv_cos, ref_cos)):
                if similar_values_iter(sv_co, ref_co):
                    # Note: Maybe this is a bit too simplistic, should we use real shape base here? Though FBX does not
                    #       have this at all... Anyway, this should cover most common cases imho.
                    continue
                shape_verts_co.extend(Vector(sv_co) - Vector(ref_co))
                shape_verts_idx.append(idx)

            # FBX does not like empty shapes (makes Unity crash e.g.).
            # To prevent this, we add a vertex that does nothing, but it keeps the shape key intact
            if not shape_verts_co:
                shape_verts_co.extend((0, 0, 0))
                shape_verts_idx.append(0)

            channel_key, geom_key = get_blender_mesh_shape_channel_key(me, shape)
            data = (channel_key, geom_key, shape_verts_co, shape_verts_idx)
            data_deformers_shape.setdefault(me, (me_key, shapes_key, OrderedDict()))[2][shape] = data

    perfmon.step("FBX export prepare: Wrapping Armatures...")

    # Armatures!
    data_deformers_skin = OrderedDict()
    data_bones = OrderedDict()
    arm_parents = set()
    for ob_obj in tuple(objects):
        if not (ob_obj.is_object and ob_obj.type in {'ARMATURE'}):
            continue
        fbx_skeleton_from_armature(scene, settings, ob_obj, objects, data_meshes,
                                   data_bones, data_deformers_skin, data_empties, arm_parents)

    # Generate leaf bones
    data_leaf_bones = []
    if settings.add_leaf_bones:
        data_leaf_bones = fbx_generate_leaf_bones(settings, data_bones)

    perfmon.step("FBX export prepare: Wrapping World...")

    # Some world settings are embedded in FBX materials...
    if scene.world:
        data_world = OrderedDict(((scene.world, get_blenderID_key(scene.world)),))
    else:
        data_world = OrderedDict()

    perfmon.step("FBX export prepare: Wrapping Materials...")

    # TODO: Check all the mat stuff works even when mats are linked to Objects
    #       (we can then have the same mesh used with different materials...).
    #       *Should* work, as FBX always links its materials to Models (i.e. objects).
    #       XXX However, material indices would probably break...
    data_materials = OrderedDict()
    for ob_obj in objects:
        # If obj is not a valid object for materials, wrapper will just return an empty tuple...
        for mat_s in ob_obj.material_slots:
            mat = mat_s.material
            if mat is None:
                continue  # Empty slots!
            # Note theoretically, FBX supports any kind of materials, even GLSL shaders etc.
            # However, I doubt anything else than Lambert/Phong is really portable!
            # We support any kind of 'surface' shader though, better to have some kind of default Lambert than nothing.
            # Note we want to keep a 'dummy' empty mat even when we can't really support it, see T41396.
            mat_data = data_materials.get(mat)
            if mat_data is not None:
                mat_data[1].append(ob_obj)
            else:
                data_materials[mat] = (get_blenderID_key(mat), [ob_obj])

    perfmon.step("FBX export prepare: Wrapping Textures...")

    # Note FBX textures also hold their mapping info.
    # TODO: Support layers?
    data_textures = OrderedDict()
    # FbxVideo also used to store static images...
    data_videos = OrderedDict()
    # For now, do not use world textures, don't think they can be linked to anything FBX wise...
    for mat in data_materials.keys():
        if check_skip_material(mat):
            continue
        for tex, use_tex in zip(mat.texture_slots, mat.use_textures):
            if tex is None or tex.texture is None or not use_tex:
                continue
            # For now, only consider image textures.
            # Note FBX does has support for procedural, but this is not portable at all (opaque blob),
            # so not useful for us.
            # TODO I think ENVIRONMENT_MAP should be usable in FBX as well, but for now let it aside.
            # if tex.texture.type not in {'IMAGE', 'ENVIRONMENT_MAP'}:
            if tex.texture.type not in {'IMAGE'}:
                continue
            img = tex.texture.image
            if img is None:
                continue
            # Find out whether we can actually use this texture for this material, in FBX context.
            tex_fbx_props = fbx_mat_properties_from_texture(tex)
            if not tex_fbx_props:
                continue
            tex_data = data_textures.get(tex)
            if tex_data is not None:
                tex_data[1][mat] = tex_fbx_props
            else:
                data_textures[tex] = (get_blenderID_key(tex), OrderedDict(((mat, tex_fbx_props),)))
            vid_data = data_videos.get(img)
            if vid_data is not None:
                vid_data[1].append(tex)
            else:
                data_videos[img] = (get_blenderID_key(img), [tex])

    perfmon.step("FBX export prepare: Wrapping Animations...")

    # Animation...
    animations = ()
    animated = set()
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    if settings.bake_anim:
        # From objects & bones only for a start.
        # Kind of hack, we need a temp scene_data for object's space handling to bake animations...
        tmp_scdata = FBXExportData(
            None, None, None,
            settings, scene, objects, None, None, 0.0, 0.0,
            data_empties, data_lamps, data_cameras, data_meshes, None,
            data_bones, data_leaf_bones, data_deformers_skin, data_deformers_shape,
            data_world, data_materials, data_textures, data_videos,
        )
        animations, animated, frame_start, frame_end = fbx_animations(tmp_scdata)

    # ##### Creation of templates...

    perfmon.step("FBX export prepare: Generating templates...")

    templates = OrderedDict()
    templates[b"GlobalSettings"] = fbx_template_def_globalsettings(scene, settings, nbr_users=1)

    if data_empties:
        templates[b"Null"] = fbx_template_def_null(scene, settings, nbr_users=len(data_empties))

    if data_lamps:
        templates[b"Light"] = fbx_template_def_light(scene, settings, nbr_users=len(data_lamps))

    if data_cameras:
        templates[b"Camera"] = fbx_template_def_camera(scene, settings, nbr_users=len(data_cameras))

    if data_bones:
        templates[b"Bone"] = fbx_template_def_bone(scene, settings, nbr_users=len(data_bones))

    if data_meshes:
        nbr = len({me_key for me_key, _me, _free in data_meshes.values()})
        if data_deformers_shape:
            nbr += sum(len(shapes[2]) for shapes in data_deformers_shape.values())
        templates[b"Geometry"] = fbx_template_def_geometry(scene, settings, nbr_users=nbr)

    if objects:
        templates[b"Model"] = fbx_template_def_model(scene, settings, nbr_users=len(objects))

    if arm_parents:
        # Number of Pose|BindPose elements should be the same as number of meshes-parented-to-armatures
        templates[b"BindPose"] = fbx_template_def_pose(scene, settings, nbr_users=len(arm_parents))

    if data_deformers_skin or data_deformers_shape:
        nbr = 0
        if data_deformers_skin:
            nbr += len(data_deformers_skin)
            nbr += sum(len(clusters) for def_me in data_deformers_skin.values() for a, b, clusters in def_me.values())
        if data_deformers_shape:
            nbr += len(data_deformers_shape)
            nbr += sum(len(shapes[2]) for shapes in data_deformers_shape.values())
        assert(nbr != 0)
        templates[b"Deformers"] = fbx_template_def_deformer(scene, settings, nbr_users=nbr)

    # No world support in FBX...
    """
    if data_world:
        templates[b"World"] = fbx_template_def_world(scene, settings, nbr_users=len(data_world))
    """

    if data_materials:
        templates[b"Material"] = fbx_template_def_material(scene, settings, nbr_users=len(data_materials))

    if data_textures:
        templates[b"TextureFile"] = fbx_template_def_texture_file(scene, settings, nbr_users=len(data_textures))

    if data_videos:
        templates[b"Video"] = fbx_template_def_video(scene, settings, nbr_users=len(data_videos))

    if animations:
        nbr_astacks = len(animations)
        nbr_acnodes = 0
        nbr_acurves = 0
        for _astack_key, astack, _al, _n, _fs, _fe in animations:
            for _alayer_key, alayer in astack.values():
                for _acnode_key, acnode, _acnode_name in alayer.values():
                    nbr_acnodes += 1
                    for _acurve_key, _dval, acurve, acurve_valid in acnode.values():
                        if acurve:
                            nbr_acurves += 1

        templates[b"AnimationStack"] = fbx_template_def_animstack(scene, settings, nbr_users=nbr_astacks)
        # Would be nice to have one layer per animated object, but this seems tricky and not that well supported.
        # So for now, only one layer per anim stack.
        templates[b"AnimationLayer"] = fbx_template_def_animlayer(scene, settings, nbr_users=nbr_astacks)
        templates[b"AnimationCurveNode"] = fbx_template_def_animcurvenode(scene, settings, nbr_users=nbr_acnodes)
        templates[b"AnimationCurve"] = fbx_template_def_animcurve(scene, settings, nbr_users=nbr_acurves)

    templates_users = sum(tmpl.nbr_users for tmpl in templates.values())

    # ##### Creation of connections...

    perfmon.step("FBX export prepare: Generating Connections...")

    connections = []

    # Objects (with classical parenting).
    for ob_obj in objects:
        # Bones are handled later.
        if not ob_obj.is_bone:
            par_obj = ob_obj.parent
            # Meshes parented to armature are handled separately, yet we want the 'no parent' connection (0).
            if par_obj and ob_obj.has_valid_parent(objects) and (par_obj, ob_obj) not in arm_parents:
                connections.append((b"OO", ob_obj.fbx_uuid, par_obj.fbx_uuid, None))
            else:
                connections.append((b"OO", ob_obj.fbx_uuid, 0, None))

    # Armature & Bone chains.
    for bo_obj in data_bones.keys():
        par_obj = bo_obj.parent
        if par_obj not in objects:
            continue
        connections.append((b"OO", bo_obj.fbx_uuid, par_obj.fbx_uuid, None))

    # Object data.
    for ob_obj in objects:
        if ob_obj.is_bone:
            bo_data_key = data_bones[ob_obj]
            connections.append((b"OO", get_fbx_uuid_from_key(bo_data_key), ob_obj.fbx_uuid, None))
        else:
            if ob_obj.type == 'LAMP':
                lamp_key = data_lamps[ob_obj.bdata.data]
                connections.append((b"OO", get_fbx_uuid_from_key(lamp_key), ob_obj.fbx_uuid, None))
            elif ob_obj.type == 'CAMERA':
                cam_key = data_cameras[ob_obj]
                connections.append((b"OO", get_fbx_uuid_from_key(cam_key), ob_obj.fbx_uuid, None))
            elif ob_obj.type == 'EMPTY' or ob_obj.type == 'ARMATURE':
                empty_key = data_empties[ob_obj]
                connections.append((b"OO", get_fbx_uuid_from_key(empty_key), ob_obj.fbx_uuid, None))
            elif ob_obj.type in BLENDER_OBJECT_TYPES_MESHLIKE:
                mesh_key, _me, _free = data_meshes[ob_obj]
                connections.append((b"OO", get_fbx_uuid_from_key(mesh_key), ob_obj.fbx_uuid, None))

    # Leaf Bones
    for (_node_name, par_uuid, node_uuid, attr_uuid, _matrix, _hide, _size) in data_leaf_bones:
        connections.append((b"OO", node_uuid, par_uuid, None))
        connections.append((b"OO", attr_uuid, node_uuid, None))

    # 'Shape' deformers (shape keys, only for meshes currently)...
    for me_key, shapes_key, shapes in data_deformers_shape.values():
        # shape -> geometry
        connections.append((b"OO", get_fbx_uuid_from_key(shapes_key), get_fbx_uuid_from_key(me_key), None))
        for channel_key, geom_key, _shape_verts_co, _shape_verts_idx in shapes.values():
            # shape channel -> shape
            connections.append((b"OO", get_fbx_uuid_from_key(channel_key), get_fbx_uuid_from_key(shapes_key), None))
            # geometry (keys) -> shape channel
            connections.append((b"OO", get_fbx_uuid_from_key(geom_key), get_fbx_uuid_from_key(channel_key), None))

    # 'Skin' deformers (armature-to-geometry, only for meshes currently)...
    for arm, deformed_meshes in data_deformers_skin.items():
        for me, (skin_key, ob_obj, clusters) in deformed_meshes.items():
            # skin -> geometry
            mesh_key, _me, _free = data_meshes[ob_obj]
            assert(me == _me)
            connections.append((b"OO", get_fbx_uuid_from_key(skin_key), get_fbx_uuid_from_key(mesh_key), None))
            for bo_obj, clstr_key in clusters.items():
                # cluster -> skin
                connections.append((b"OO", get_fbx_uuid_from_key(clstr_key), get_fbx_uuid_from_key(skin_key), None))
                # bone -> cluster
                connections.append((b"OO", bo_obj.fbx_uuid, get_fbx_uuid_from_key(clstr_key), None))

    # Materials
    mesh_mat_indices = OrderedDict()
    _objs_indices = {}
    for mat, (mat_key, ob_objs) in data_materials.items():
        for ob_obj in ob_objs:
            connections.append((b"OO", get_fbx_uuid_from_key(mat_key), ob_obj.fbx_uuid, None))
            # Get index of this mat for this object (or dupliobject).
            # Mat indices for mesh faces are determined by their order in 'mat to ob' connections.
            # Only mats for meshes currently...
            # Note in case of dupliobjects a same me/mat idx will be generated several times...
            # Should not be an issue in practice, and it's needed in case we export duplis but not the original!
            if ob_obj.type not in BLENDER_OBJECT_TYPES_MESHLIKE:
                continue
            _mesh_key, me, _free = data_meshes[ob_obj]
            idx = _objs_indices[ob_obj] = _objs_indices.get(ob_obj, -1) + 1
            mesh_mat_indices.setdefault(me, OrderedDict())[mat] = idx
    del _objs_indices

    # Textures
    for tex, (tex_key, mats) in data_textures.items():
        for mat, fbx_mat_props in mats.items():
            mat_key, _ob_objs = data_materials[mat]
            for fbx_prop in fbx_mat_props:
                # texture -> material properties
                connections.append((b"OP", get_fbx_uuid_from_key(tex_key), get_fbx_uuid_from_key(mat_key), fbx_prop))

    # Images
    for vid, (vid_key, texs) in data_videos.items():
        for tex in texs:
            tex_key, _texs = data_textures[tex]
            connections.append((b"OO", get_fbx_uuid_from_key(vid_key), get_fbx_uuid_from_key(tex_key), None))

    # Animations
    for astack_key, astack, alayer_key, _name, _fstart, _fend in animations:
        # Animstack itself is linked nowhere!
        astack_id = get_fbx_uuid_from_key(astack_key)
        # For now, only one layer!
        alayer_id = get_fbx_uuid_from_key(alayer_key)
        connections.append((b"OO", alayer_id, astack_id, None))
        for elem_key, (alayer_key, acurvenodes) in astack.items():
            elem_id = get_fbx_uuid_from_key(elem_key)
            # Animlayer -> animstack.
            # alayer_id = get_fbx_uuid_from_key(alayer_key)
            # connections.append((b"OO", alayer_id, astack_id, None))
            for fbx_prop, (acurvenode_key, acurves, acurvenode_name) in acurvenodes.items():
                # Animcurvenode -> animalayer.
                acurvenode_id = get_fbx_uuid_from_key(acurvenode_key)
                connections.append((b"OO", acurvenode_id, alayer_id, None))
                # Animcurvenode -> object property.
                connections.append((b"OP", acurvenode_id, elem_id, fbx_prop.encode()))
                for fbx_item, (acurve_key, default_value, acurve, acurve_valid) in acurves.items():
                    if acurve:
                        # Animcurve -> Animcurvenode.
                        connections.append((b"OP", get_fbx_uuid_from_key(acurve_key), acurvenode_id, fbx_item.encode()))

    perfmon.level_down()

    # ##### And pack all this!

    return FBXExportData(
        templates, templates_users, connections,
        settings, scene, objects, animations, animated, frame_start, frame_end,
        data_empties, data_lamps, data_cameras, data_meshes, mesh_mat_indices,
        data_bones, data_leaf_bones, data_deformers_skin, data_deformers_shape,
        data_world, data_materials, data_textures, data_videos,
    )
