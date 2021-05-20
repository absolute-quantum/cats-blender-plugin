# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: Hotox
# Edits by: Hotox

import bpy
import typing

__bl_classes = []
__bl_ordered_classes = []
__make_annotations = (not bpy.app.version < (2, 79, 9))


def register_wrap(cls):
    if hasattr(cls, 'bl_rna'):
        __bl_classes.append(cls)
    cls = make_annotations(cls)
    return cls


def make_annotations(cls):
    if __make_annotations:
        if bpy.app.version < (2, 93, 0):
            bl_props = {k:v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
        else:
            bl_props = {k:v for k, v in cls.__dict__.items() if isinstance(v, bpy.props._PropertyDeferred)}
        if bl_props:
            if '__annotations__' not in cls.__dict__:
                setattr(cls, '__annotations__', {})
            annotations = cls.__dict__['__annotations__']
            for k, v in bl_props.items():
                annotations[k] = v
                delattr(cls, k)
    return cls


def order_classes():
    global __bl_ordered_classes
    deps_dict = {}
    classes_to_register = set(iter_classes_to_register())
    for cls in classes_to_register:
        deps_dict[cls] = set(iter_own_register_deps(cls, classes_to_register))

    # Put all the UI into the list first
    __bl_ordered_classes = []
    for cls in __bl_classes:
        if cls.__module__.startswith('ui.'):
            __bl_ordered_classes.append(cls)

    # Then put everything else sorted into the list
    for cls in toposort(deps_dict):
        if not cls.__module__.startswith('ui.'):
            __bl_ordered_classes.append(cls)


def iter_classes_to_register():
    for cls in __bl_classes:
        yield cls


def iter_own_register_deps(cls, own_classes):
    yield from (dep for dep in iter_register_deps(cls) if dep in own_classes)


def iter_register_deps(cls):
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            yield dependency


def get_dependency_from_annotation(value):
    if isinstance(value, tuple) and len(value) == 2:
        if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
            return value[1]["type"]
    return None


# Find order to register to solve dependencies
#################################################

def toposort(deps_dict):
    sorted_list = []
    sorted_values = set()
    while len(deps_dict) > 0:
        unsorted = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        deps_dict = {value : deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list
