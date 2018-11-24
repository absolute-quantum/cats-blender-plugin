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

__bl_classes = []
__make_annotations = (not bpy.app.version < (2, 79, 9))


def register_wrap(cls):
    if __make_annotations:
        bl_props = {k:v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
        if bl_props:
            if '__annotations__' not in cls.__dict__:
                setattr(cls, '__annotations__', {})
            annotations = cls.__dict__['__annotations__']
            for k, v in bl_props.items():
                annotations[k] = v
                delattr(cls, k)
    if hasattr(cls, 'bl_rna'):
        __bl_classes.append(cls)
    return cls
