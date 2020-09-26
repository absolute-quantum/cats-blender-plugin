# Thanks to https://www.thegrove3d.com/learn/how-to-translate-a-blender-addon/ for the idea

from bpy.app.translations import locale

if locale in ['ja_JP']:
    from .ja_JP import dictionary
else:
    from .en_US import dictionary


def t(phrase: str, *args, **kwargs):
    # Translate the given phrase into Blender's current language.
    try:
        output = dictionary[phrase]
        if isinstance(output, list):
            newList = []
            for string in output:
                newList.append(string.format(*args, **kwargs))
            return newList
        elif not isinstance(output, str):
            return output
        else:
            return output.format(*args, **kwargs)
    except KeyError:
        print('Warning - Text missing for: ' + phrase)
    return phrase
