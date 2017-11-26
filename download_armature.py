import os
import urllib


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
}

# Download them
for name in download_data:
    url = download_data[name]
    filename = str('armature.' + str(name) + '.blend')
    new_file_path = os.path.join(os.path.dirname(__file__), 'tests', 'armatures', 'armature.' + str(name) + '.blend')
    if exists(new_file_path):
        print('Skipping downloading ' + filename + ' because it exists')
    else:
        print('Downloading ' + filename + ' because it doesn\'t exists')
        urllib.urlretrieve(url, new_file_path)
