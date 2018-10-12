"""A conversion module for googletrans"""
from __future__ import print_function
import re
import json


def build_params(query, src, dest, token):
    params = {
        'client': 't',
        'sl': src,
        'tl': dest,
        'hl': dest,
        'dt': ['at', 'bd', 'ex', 'ld', 'md', 'qca', 'rw', 'rm', 'ss', 't'],
        'ie': 'UTF-8',
        'oe': 'UTF-8',
        'otf': 1,
        'ssel': 0,
        'tsel': 0,
        'tk': token,
        'q': query,
    }
    return params


def legacy_format_json(original):
    # save state
    states = []
    text = original
    
    # save position for double-quoted texts
    for i, pos in enumerate(re.finditer('"', text)):
        # pos.start() is a double-quote
        p = pos.start() + 1
        if i % 2 == 0:
            nxt = text.find('"', p)
            states.append((p, text[p:nxt]))

    # replace all weired characters in text
    while text.find(',,') > -1:
        text = text.replace(',,', ',null,')
    while text.find('[,') > -1:
        text = text.replace('[,', '[null,')

    # recover state
    for i, pos in enumerate(re.finditer('"', text)):
        p = pos.start() + 1
        if i % 2 == 0:
            j = int(i / 2)
            nxt = text.find('"', p)
            # replacing a portion of a string
            # use slicing to extract those parts of the original string to be kept
            text = text[:p] + states[j][1] + text[nxt:]

    try:
        converted = json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(text)

    return converted


def format_json(original):
    #original = '<!DOCTYPE html><html lang=en><meta charset=utf-8><meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width"><title>Error 403 (Forbidden)!!1</title><style>*{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo{background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat 0% 0%/100% 100%;-moz-border-image:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) 0}}@media only screen and (-webkit-min-device-pixel-ratio:2){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat;-webkit-background-size:100% 100%}}#logo{display:inline-block;height:54px;width:150px}</style><a href=//www.google.com/><span id=logo aria-label=Google></span></a><p><b>403.</b> <ins>That’s an error.</ins><p>Your client does not have permission to get URL <code>/translate_a/single?client=t&amp;sl=auto&amp;tl=en&amp;hl=en&amp;dt=at&amp;dt=bd&amp;dt=ex&amp;dt=ld&amp;dt=md&amp;dt=qca&amp;dt=rw&amp;dt=rm&amp;dt=ss&amp;dt=t&amp;ie=UTF-8&amp;oe=UTF-8&amp;otf=1&amp;ssel=0&amp;tsel=0&amp;tk=684737.684737&amp;q=test</code> from this server.  <ins>That’s all we know.</ins></p></p></a></meta></meta></html></!DOCTYPE>'
    try:
        converted = json.loads(original)
    except ValueError:
        converted = legacy_format_json(original)
    return converted


def rshift(val, n):
    """python port for '>>>'(right shift with padding)
    """
    return (val % 0x100000000) >> n
