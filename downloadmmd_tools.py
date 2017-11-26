import requests
import zipfile
import StringIO
import os

r = requests.get('https://github.com/powroupi/blender_mmd_tools/archive/dev_test.zip', stream=True)
z = zipfile.ZipFile(StringIO.StringIO(r.content))
z.extractall(os.path.join(os.path.dirname(__file__), 'tmp', 'mmd_tools'))
