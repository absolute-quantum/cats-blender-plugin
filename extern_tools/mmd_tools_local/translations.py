# -*- coding: utf-8 -*-

import bpy
import csv

jp_half_to_full_tuples = (
    ('ｳﾞ', 'ヴ'), ('ｶﾞ', 'ガ'), ('ｷﾞ', 'ギ'), ('ｸﾞ', 'グ'), ('ｹﾞ', 'ゲ'),
    ('ｺﾞ', 'ゴ'), ('ｻﾞ', 'ザ'), ('ｼﾞ', 'ジ'), ('ｽﾞ', 'ズ'), ('ｾﾞ', 'ゼ'),
    ('ｿﾞ', 'ゾ'), ('ﾀﾞ', 'ダ'), ('ﾁﾞ', 'ヂ'), ('ﾂﾞ', 'ヅ'), ('ﾃﾞ', 'デ'),
    ('ﾄﾞ', 'ド'), ('ﾊﾞ', 'バ'), ('ﾊﾟ', 'パ'), ('ﾋﾞ', 'ビ'), ('ﾋﾟ', 'ピ'),
    ('ﾌﾞ', 'ブ'), ('ﾌﾟ', 'プ'), ('ﾍﾞ', 'ベ'), ('ﾍﾟ', 'ペ'), ('ﾎﾞ', 'ボ'),
    ('ﾎﾟ', 'ポ'), ('｡', '。'), ('｢', '「'), ('｣', '」'), ('､', '、'),
    ('･', '・'), ('ｦ', 'ヲ'), ('ｧ', 'ァ'), ('ｨ', 'ィ'), ('ｩ', 'ゥ'),
    ('ｪ', 'ェ'), ('ｫ', 'ォ'), ('ｬ', 'ャ'), ('ｭ', 'ュ'), ('ｮ', 'ョ'),
    ('ｯ', 'ッ'), ('ｰ', 'ー'), ('ｱ', 'ア'), ('ｲ', 'イ'), ('ｳ', 'ウ'),
    ('ｴ', 'エ'), ('ｵ', 'オ'), ('ｶ', 'カ'), ('ｷ', 'キ'), ('ｸ', 'ク'),
    ('ｹ', 'ケ'), ('ｺ', 'コ'), ('ｻ', 'サ'), ('ｼ', 'シ'), ('ｽ', 'ス'),
    ('ｾ', 'セ'), ('ｿ', 'ソ'), ('ﾀ', 'タ'), ('ﾁ', 'チ'), ('ﾂ', 'ツ'),
    ('ﾃ', 'テ'), ('ﾄ', 'ト'), ('ﾅ', 'ナ'), ('ﾆ', 'ニ'), ('ﾇ', 'ヌ'),
    ('ﾈ', 'ネ'), ('ﾉ', 'ノ'), ('ﾊ', 'ハ'), ('ﾋ', 'ヒ'), ('ﾌ', 'フ'),
    ('ﾍ', 'ヘ'), ('ﾎ', 'ホ'), ('ﾏ', 'マ'), ('ﾐ', 'ミ'), ('ﾑ', 'ム'),
    ('ﾒ', 'メ'), ('ﾓ', 'モ'), ('ﾔ', 'ヤ'), ('ﾕ', 'ユ'), ('ﾖ', 'ヨ'),
    ('ﾗ', 'ラ'), ('ﾘ', 'リ'), ('ﾙ', 'ル'), ('ﾚ', 'レ'), ('ﾛ', 'ロ'),
    ('ﾜ', 'ワ'), ('ﾝ', 'ン'),
    )

jp_to_en_tuples = [
  ('全ての親', 'ParentNode'),
  ('操作中心', 'ControlNode'),               
  ('センター', 'Center'),
  ('ｾﾝﾀｰ', 'Center'),
  ('グループ', 'Group'),
  ('グルーブ', 'Groove'),
  ('キャンセル', 'Cancel'),
  ('上半身', 'UpperBody'),
  ('下半身', 'LowerBody'),
  ('手首', 'Wrist'),
  ('足首', 'Ankle'),
  ('首', 'Neck'),
  ('頭', 'Head'),
  ('顔', 'Face'),
  ('下顎', 'Chin'),
  ('下あご', 'Chin'),
  ('あご', 'Jaw'),
  ('顎', 'Jaw'),
  ('両目', 'Eyes'),
  ('目', 'Eye'),
  ('眉', 'Eyebrow'),
  ('舌', 'Tongue'),
  ('涙', 'Tears'),
  ('泣き', 'Cry'),
  ('歯', 'Teeth'),
  ('照れ', 'Blush'),
  ('青ざめ', 'Pale'),
  ('ガーン', 'Gloom'),
  ('汗', 'Sweat'),
  ('怒', 'Anger'),
  ('感情', 'Emotion'),
  ('符', 'Marks'),
  ('暗い', 'Dark'),
  ('腰', 'Waist'),
  ('髪', 'Hair'),  
  ('三つ編み', 'Braid'),
  ('胸', 'Breast'),
  ('乳', 'Boob'),
  ('おっぱい', 'Tits'),
  ('筋', 'Muscle'),
  ('腹', 'Belly'),
  ('鎖骨', 'Clavicle'),
  ('肩', 'Shoulder'),
  ('腕', 'Arm'),
  ('うで', 'Arm'),
  ('ひじ', 'Elbow'),
  ('肘', 'Elbow'),
  ('手', 'Hand'),
  ('親指', 'Thumb'),
  ('人指', 'IndexFinger'),
  ('人差指', 'IndexFinger'),
  ('中指', 'MiddleFinger'),
  ('薬指', 'RingFinger'),
  ('小指', 'LittleFinger'),  
  ('足', 'Leg'),
  ('ひざ', 'Knee'),  
  ('つま', 'Toe'),
  ('袖', 'Sleeve'),
  ('新規', 'New'),
  ('ボーン', 'Bone'),
  ('捩', 'Twist'),
  ('回転', 'Rotation'),
  ('軸', 'Axis'),
  ('ﾈｸﾀｲ', 'Necktie'),
  ('ネクタイ', 'Necktie'),
  ('ヘッドセット', 'Headset'),
  ('飾り', 'Accessory'),
  ('リボン', 'Ribbon'),
  ('襟', 'Collar'),
  ('紐', 'String'),
  ('コード', 'Cord'),
  ('イヤリング', 'Earring'),
  ('メガネ', 'Eyeglasses'),
  ('眼鏡', 'Glasses'),
  ('帽子', 'Hat'),
  ('ｽｶｰﾄ', 'Skirt'),
  ('スカート', 'Skirt'),
  ('パンツ', 'Pantsu'),
  ('シャツ', 'Shirt'),
  ('フリル', 'Frill'),
  ('マフラー', 'Muffler'),
  ('ﾏﾌﾗｰ', 'Muffler'),
  ('服', 'Clothes'),
  ('ブーツ', 'Boots'),
  ('ねこみみ', 'CatEars'),
  ('ジップ', 'Zip'),
  ('ｼﾞｯﾌﾟ', 'Zip'),
  ('ダミー', 'Dummy'),
  ('ﾀﾞﾐｰ', 'Dummy'),
  ('基', 'Category'),
  ('あほ毛', 'Antenna'),
  ('アホ毛', 'Antenna'),
  ('モミアゲ', 'Sideburn'),
  ('もみあげ', 'Sideburn'),
  ('ツインテ', 'Twintail'),
  ('おさげ', 'Pigtail'),
  ('ひらひら', 'Flutter'),
  ('調整', 'Adjustment'),
  ('補助', 'Aux'),
  ('右', 'Right'),
  ('左', 'Left'),  
  ('前', 'Front'),
  ('後ろ', 'Behind'),
  ('後', 'Back'),
  ('横', 'Side'),
  ('中', 'Middle'),
  ('上', 'Upper'),
  ('下', 'Lower'),
  ('親', 'Parent'),  
  ('先', 'Tip'),
  ('パーツ', 'Part'),
  ('光', 'Light'),
  ('戻', 'Return'),
  ('羽', 'Wing'),
  ('根', 'Base'), # ideally 'Root' but to avoid confusion
  ('毛', 'Strand'),
  ('尾', 'Tail'),
  ('尻', 'Butt'),
  # full-width unicode forms I think: https://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms
  ('０', '0'), ('１', '1'), ('２', '2'), ('３', '3'), ('４', '4'), ('５', '5'), ('６', '6'), ('７', '7'), ('８', '8'), ('９', '9'),
  ('ａ', 'a'), ('ｂ', 'b'), ('ｃ', 'c'), ('ｄ', 'd'), ('ｅ', 'e'), ('ｆ', 'f'), ('ｇ', 'g'), ('ｈ', 'h'), ('ｉ', 'i'), ('ｊ', 'j'),
  ('ｋ', 'k'), ('ｌ', 'l'), ('ｍ', 'm'), ('ｎ', 'n'), ('ｏ', 'o'), ('ｐ', 'p'), ('ｑ', 'q'), ('ｒ', 'r'), ('ｓ', 's'), ('ｔ', 't'), 
  ('ｕ', 'u'), ('ｖ', 'v'), ('ｗ', 'w'), ('ｘ', 'x'), ('ｙ', 'y'), ('ｚ', 'z'),
  ('Ａ', 'A'), ('Ｂ', 'B'), ('Ｃ', 'C'), ('Ｄ', 'D'), ('Ｅ', 'E'), ('Ｆ', 'F'), ('Ｇ', 'G'), ('Ｈ', 'H'), ('Ｉ', 'I'), ('Ｊ', 'J'),
  ('Ｋ', 'K'), ('Ｌ', 'L'), ('Ｍ', 'M'), ('Ｎ', 'N'), ('Ｏ', 'O'), ('Ｐ', 'P'), ('Ｑ', 'Q'), ('Ｒ', 'R'), ('Ｓ', 'S'), ('Ｔ', 'T'), 
  ('Ｕ', 'U'), ('Ｖ', 'V'), ('Ｗ', 'W'), ('Ｘ', 'X'), ('Ｙ', 'Y'), ('Ｚ', 'Z'),
  ('＋', '+'), ('－', '-'), ('＿', '_'), ('／', '/'),
  ('.', '_'), # probably should be combined with the global 'use underscore' option
 ]

def translateFromJp(name):
    for tuple in jp_to_en_tuples:
        if tuple[0] in name:
            name = name.replace(tuple[0], tuple[1])
    return name


def getTranslator(csvfile='', keep_order=False):
    translator = MMDTranslator()
    if isinstance(csvfile, bpy.types.Text):
        translator.load_from_stream(csvfile)
    elif isinstance(csvfile, dict):
        translator.csv_tuples.extend(csvfile.items())
    elif csvfile in bpy.data.texts.keys():
        translator.load_from_stream(bpy.data.texts[csvfile])
    else:
        translator.load(csvfile)

    if not keep_order:
        translator.sort()
    translator.update()
    return translator

class MMDTranslator:

    def __init__(self):
        self.__csv_tuples = []
        self.__fails = {}

    @staticmethod
    def default_csv_filepath():
        return __file__[:-3]+'.csv'

    @staticmethod
    def get_csv_text(text_name=None):
        text_name = text_name or bpy.path.basename(MMDTranslator.default_csv_filepath())
        csv_text = bpy.data.texts.get(text_name, None)
        if csv_text is None:
            csv_text = bpy.data.texts.new(text_name)
        return csv_text

    @staticmethod
    def replace_from_tuples(name, tuples):
        for pair in tuples:
            if pair[0] in name:
                name = name.replace(pair[0], pair[1])
        return name

    @property
    def csv_tuples(self):
        return self.__csv_tuples

    @property
    def fails(self):
        return self.__fails

    def sort(self):
        self.__csv_tuples.sort(key=lambda row: (-len(row[0]), row))

    def update(self):
        from collections import OrderedDict
        count_old = len(self.__csv_tuples)
        tuples_dict = OrderedDict((row[0], row) for row in self.__csv_tuples if len(row) >= 2 and row[0])
        self.__csv_tuples.clear()
        self.__csv_tuples.extend(tuples_dict.values())
        print(' - removed items:', count_old-len(self.__csv_tuples), '(of %d)'%count_old)

    def half_to_full(self, name):
        return self.replace_from_tuples(name, jp_half_to_full_tuples)

    def is_translated(self, name):
        try:
            name.encode('ascii', errors='strict')
        except UnicodeEncodeError:
            return False
        return True

    def translate(self, name, default=None, from_full_width=True):
        if from_full_width:
            name = self.half_to_full(name)
        name_new = self.replace_from_tuples(name, self.__csv_tuples)
        if default is not None and not self.is_translated(name_new):
            self.__fails[name] = name_new
            return default
        return name_new

    def save_fails(self, text_name=None):
        text_name = text_name or (__name__+'.fails')
        txt = self.get_csv_text(text_name)
        fmt = '"%s","%s"'
        items = sorted(self.__fails.items(), key=lambda row: (-len(row[0]), row))
        txt.from_string('\n'.join(fmt%(k, v) for k, v in items))
        return txt

    def load_from_stream(self, csvfile=None):
        csvfile = csvfile or self.get_csv_text()
        if isinstance(csvfile, bpy.types.Text):
            csvfile = (l.body+'\n' for l in csvfile.lines)
        spamreader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        csv_tuples = [tuple(row) for row in spamreader if len(row) >= 2]
        self.__csv_tuples = csv_tuples
        print(' - load items:', len(self.__csv_tuples))

    def save_to_stream(self, csvfile=None):
        csvfile = csvfile or self.get_csv_text()
        lineterminator = '\r\n'
        if isinstance(csvfile, bpy.types.Text):
            csvfile.clear()
            lineterminator = '\n'
        spamwriter = csv.writer(csvfile, delimiter=',', lineterminator=lineterminator, quoting=csv.QUOTE_ALL)
        spamwriter.writerows(self.__csv_tuples)
        print(' - save items:', len(self.__csv_tuples))

    def load(self, filepath=None):
        filepath = filepath or self.default_csv_filepath()
        print('Loading csv file:', filepath)
        with open(filepath, 'rt', encoding='utf-8', newline='') as csvfile:
            self.load_from_stream(csvfile)

    def save(self, filepath=None):
        filepath = filepath or self.default_csv_filepath()
        print('Saving csv file:', filepath)
        with open(filepath, 'wt', encoding='utf-8', newline='') as csvfile:
            self.save_to_stream(csvfile)


class DictionaryEnum:
    __items_id = None
    __items_cache = None

    @staticmethod
    def get_dictionary_items(prop, context):
        id_tag = prop.as_pointer()
        if id_tag and DictionaryEnum.__items_id == id_tag:
            return DictionaryEnum.__items_cache

        DictionaryEnum.__items_id = id_tag
        DictionaryEnum.__items_cache = items = []
        if 'import' in prop.bl_rna.identifier:
            items.append(('DISABLED', 'Disabled', '', 0))

        items.append(('INTERNAL', 'Internal Dictionary', 'The dictionary defined in '+__name__, len(items)))

        for txt_name in sorted(x.name for x in bpy.data.texts if x.name.lower().endswith('.csv')):
            items.append((txt_name, txt_name, "bpy.data.texts['%s']"%txt_name, 'TEXT', len(items)))

        import os
        from mmd_tools_local.bpyutils import addon_preferences
        folder = addon_preferences('dictionary_folder', '')
        if os.path.isdir(folder):
            for filename in sorted(x for x in os.listdir(folder) if x.lower().endswith('.csv')):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    items.append((filepath, filename, filepath, 'FILE', len(items)))

        if 'dictionary' in prop:
            prop['dictionary'] = min(prop['dictionary'], len(items)-1)
        return items

    @staticmethod
    def get_translator(dictionary):
        if dictionary == 'DISABLED':
            return None
        if dictionary == 'INTERNAL':
            return getTranslator(dict(jp_to_en_tuples))
        return getTranslator(dictionary)

