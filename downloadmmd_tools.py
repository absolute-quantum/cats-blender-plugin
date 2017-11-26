import requests
import zipfile
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os
import wget

# Download mmd_tools
r = requests.get('https://github.com/powroupi/blender_mmd_tools/archive/dev_test.zip', stream=True)
z = zipfile.ZipFile(StringIO.StringIO(r.content))
z.extractall(os.path.join(os.path.dirname(__file__), 'tmp', 'mmd_tools'))

# armature.mmd1.blend
testfile = wget.download('https://www.dropbox.com/s/gvf33pxubugj3qe/armature.mmd1.blend?dl=1', os.path.join(os.path.dirname(__file__), 'tests', 'armatures', 'armature.mmd1.blend'))
