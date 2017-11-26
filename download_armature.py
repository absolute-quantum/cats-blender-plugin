import sys
import os
import urllib2

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


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
        f = urllib2.urlopen(url)
        data = f.read()
        with open(new_file_path, "wb") as code:
            code.write(data)
