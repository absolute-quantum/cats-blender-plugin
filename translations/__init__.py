# Thanks to https://www.thegrove3d.com/learn/how-to-translate-a-blender-addon/ for the idea

import os
import importlib
import addon_utils
from bpy.app.translations import locale
from .en_US import dictionary as dict_en

# Get package name, important for relative imports
package_name = ''
for mod in addon_utils.modules():
    if mod.bl_info['name'] == 'Cats Blender Plugin':
        package_name = mod.__name__

# Get all supported languages in translations folder
languages = []
for file in os.listdir(os.path.dirname(__file__)):
    lang_name = os.path.splitext(file)[0]
    if len(lang_name) == 5 and lang_name[2] == '_' and lang_name != 'en_US':
        languages.append(lang_name)

# Import the correct language dictionary
if locale in languages:
    lang = importlib.import_module(package_name + '.translations.' + locale)
    dictionary = lang.dictionary
else:
    dictionary = dict_en


def t(phrase: str, *args, **kwargs):
    # Translate the given phrase into Blender's current language.
    output = dictionary.get(phrase)
    if output is None:
       output = dict_en.get(phrase)
    if output is None:
        print('Warning: Unknown phrase: ' + phrase)
        return phrase

    if isinstance(output, list):
        newList = []
        for string in output:
            newList.append(string.format(*args, **kwargs))
        return newList
    elif not isinstance(output, str):
        return output
    else:
        return output.format(*args, **kwargs)


def check_missing_translations():
    lang_dicts = []
    for language in languages:
        lang = importlib.import_module(package_name + '.translations.' + language)
        lang_dicts.append(lang.dictionary)

    for key, value in dict_en.items():
        if value is None:
            print('Translations en_US: Value missing for key: ' + key)

        for lang_dict in lang_dicts:
            if lang_dict.get(key) is None:
                print('Translations ' + lang_dict.get('name') + ': Value missing for key: ' + key)
