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
    new_file_path = os.path.join(os.path.dirname(__file__), 'tests', 'armatures', 'armature.' + str(name) + '.blend')
    if exists(new_file_path) is False:
        print('Notice: Downloaded ' + filename + ' because it didn\'t existed')
        with urllib.request.urlopen(url) as response, open(new_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
