# Thanks to https://www.thegrove3d.com/learn/how-to-translate-a-blender-addon/ for the idea

import os
import csv
import pathlib
import addon_utils
from bpy.app.translations import locale

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
translations_file = os.path.join(resources_dir, "translations.csv")

dictionary = {}


def load_translations():
    global dictionary
    dictionary = {}

    with open (translations_file, 'r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        for row in csv_reader:
            text = row.get(locale)
            if not text:
                text = row.get('en_US')
            dictionary[row['name']] = text

    check_missing_translations()


def t(phrase: str, *args, **kwargs):
    # Translate the given phrase into Blender's current language.
    output = dictionary.get(phrase)
    if output is None:
        print('Warning: Unknown phrase: ' + phrase)
        return phrase

    return output.format(*args, **kwargs)


def check_missing_translations():
    for key, value in dictionary.items():
        if not value:
            print('Translations en_US: Value missing for key: ' + key)


load_translations()