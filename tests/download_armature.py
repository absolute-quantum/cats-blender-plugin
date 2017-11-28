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

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by:

import os
import urllib.request
import shutil


# Test whether a path exists.  Returns False for broken symbolic links
def exists(path):
    try:
        os.stat(path)
    except os.error:
        return False
    return True


# Add any test models you want here!
download_data = {
    'mmd1': 'https://www.dropbox.com/s/gvf33pxubugj3qe/armature.mmd1.blend?dl=1',
    'ryuko': 'https://www.dropbox.com/s/74fj6msbyn3c7rn/armature.ryuko.blend?dl=1',
    'bonetranslationerror': 'https://www.dropbox.com/s/ckoseplcfdozpeu/armature.translationerror.blend?dl=1',
}

# Download them
for name in download_data:
    url = download_data[name]
    filename = str('armature.' + str(name) + '.blend')
    new_file_path = os.path.join(os.path.dirname(__file__), 'armatures', 'armature.' + str(name) + '.blend')
    if exists(new_file_path) is False:
        print('Notice: Downloaded ' + filename + ' because it didn\'t existed')
        with urllib.request.urlopen(url) as response, open(new_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
