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

# Code author: Shotariya
# Repo: https://github.com/Grim-es/shotariya
# Code author: Neitri
# Repo: https://github.com/netri/blender_neitri_tools
# Edits by: GiveMeAllYourCats, Hotox

from collections import OrderedDict

bone_list = ['ControlNode', 'ParentNode', 'Center', 'CenterTip', 'Groove', 'Waist', 'Eyes', 'EyesTip',
             'LowerBodyTip', 'UpperBody2Tip', 'GrooveTip', 'NeckTip']
bone_list_with = ['_shadow_', '_dummy_', 'Dummy_', 'WaistCancel', 'LegIKParent', 'LegIK', 'LegIKTip', 'ToeTipIK',
                  'ToeTipIKTip', 'ShoulderP_', 'EyeTip_', 'ThumbTip_', 'IndexFingerTip_', 'MiddleFingerTip_',
                  'RingFingerTip_', 'LittleFingerTip_', 'HandDummy_', 'HandTip_', 'ShoulderC_', 'SleeveShoulderIK_']
bone_list_parenting = {
    'Spine': 'Hips',
    'Chest': 'Spine',
    'Neck': 'Chest',
    'Head': 'Neck',
    'Left shoulder': 'Chest',
    'Right shoulder': 'Chest',
    'Left arm': 'Left shoulder',
    'Right arm': 'Right shoulder',
    'Left elbow': 'Left arm',
    'Right elbow': 'Right arm',
    'Left wrist': 'Left elbow',
    'Right wrist': 'Right elbow',
    'Left leg': 'Hips',
    'Right leg': 'Hips',
    'Left knee': 'Left leg',
    'Right knee': 'Right leg',
    'Left ankle': 'Left knee',
    'Right ankle': 'Right knee',
    'Left toe': 'Left ankle',
    'Right toe': 'Right ankle'
}
dont_delete_these_bones = {
    'Hips', 'Spine', 'Chest', 'Neck', 'Head',
    'Left leg', 'Left knee', 'Left ankle', 'Left toe',
    'Right leg', 'Right knee', 'Right ankle', 'Right toe',
    'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist',
    'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist',
    'OldRightEye', 'OldLeftEye', 'LeftEye', 'RightEye', 'Eye_L', 'Eye_R',

    'Thumb0_R', 'Thumb1_R', 'Thumb2_R',
    'IndexFinger1_R', 'IndexFinger2_R', 'IndexFinger3_R',
    'MiddleFinger1_R', 'MiddleFinger2_R', 'MiddleFinger3_R',
    'RingFinger1_R', 'RingFinger2_R', 'RingFinger3_R',
    'LittleFinger1_R', 'LittleFinger2_R', 'LittleFinger3_R',

    'Thumb0_L', 'Thumb1_L', 'Thumb2_L',
    'IndexFinger1_L', 'IndexFinger2_L', 'IndexFinger3_L',
    'MiddleFinger1_L', 'MiddleFinger2_L', 'MiddleFinger3_L',
    'RingFinger1_L', 'RingFinger2_L', 'RingFinger3_L',
    'LittleFinger1_L', 'LittleFinger2_L', 'LittleFinger3_L',
}
bone_list_rename_unknown_side = {
    'Shoulder': 'shoulder',
    'Shoulder_001': 'shoulder'
}

################################
# Capitalize all bone names!
# Capitalize after each space!
#
# Replace New Bone Patterns:
#   Left/Right = \Left
#   L/R = \L
# Replace Old Bone Patterns:
#   Left/Right = \Left
#   left/right = \left
#   L/R = \L
#   l/r = \l
################################
bone_rename = OrderedDict()
bone_rename['Hips'] = [
    'LowerBody',
    'Lowerbody',
    'Lower Body',
    'Mixamorig:Hips',
]
bone_rename['Spine'] = [
    'UpperBody',
    'Upperbody',
    'Upper Body',
    'Upper Waist',
    'Mixamorig:Spine',
]
bone_rename['Chest'] = [
    'UpperBody2',
    'Upperbody2',
    'Upper Body 2',
    'Upper Waist 2',
    'Waist Upper 2',
    'Mixamorig:Spine1',
]
bone_rename['NewChest'] = [  # Will get deleted
    'UpperBody3',
    'Upperbody3',
    'Upper Body 3',
    'Upper Waist 3',
    'Waist Upper 3',
    'Mixamorig:Spine2',
]
bone_rename['Neck'] = [
    'Mixamorig:Neck',
]
bone_rename['Head'] = [
    'Mixamorig:Head',
]
bone_rename['\Left shoulder'] = [
    '\Left Shoulder',
    '\LeftShoulder',
    'Shoulder_\L',
    'Mixamorig:\LeftShoulder',
]
bone_rename['\Left arm'] = [
    '\Left Arm',
    '\LeftArm',
    'Arm_\L',
    'Mixamorig:\LeftArm',
]
bone_rename['\Left elbow'] = [
    '\Left Elbow',
    '\LeftElbow',
    'Elbow_\L',
    'Mixamorig:\LeftForeArm',
]
bone_rename['\Left wrist'] = [
    '\Left Wrist',
    '\LeftWrist',
    'Wrist_\L',
    'Mixamorig:\LeftHand',
]
bone_rename['\Left leg'] = [
    '\Left Leg',
    '\Left foot',
    '\LeftLeg',
    'Leg_\L',
    'Mixamorig:\LeftUpLeg',
]
bone_rename['\Left knee'] = [
    '\Left Knee',
    '\LeftKnee',
    'Knee_\L',
    'Mixamorig:\LeftLeg',
]
bone_rename['\Left ankle'] = [
    '\Left Ankle',
    '\LeftAnkle',
    'Ankle_\L',
    'Mixamorig:\LeftFoot',
]
bone_rename['\Left toe'] = [
    '\Left Toe',
    '\LeftToe',
    '\Left Toe EX',
    '\Left Foot Tip EX',
    'LegTipEX_\L',
    'ClawTipEX_\L',
    'Mixamorig:\LeftToeBase',
]
bone_rename['Eye_\L'] = [
    'Mixamorig:\LeftEye',
]

################################
# Capitalize all bone names!
# Capitalize after each space!
#
# Replace New Bone Patterns:
#   Left/Right = \Left
#   L/R = \L
# Replace Old Bone Patterns:
#   Left/Right = \Left
#   left/right = \left
#   L/R = \L
#   l/r = \l
################################
bone_reweight = OrderedDict()
bone_reweight['Hips'] = [
    'LowerBody1',
    'Lowerbody2',
]
bone_reweight['Spine'] = [
    'UpperBodyx',
]
bone_reweight['Chest'] = [
    'UpperBodyx2',
]
bone_reweight['Neck'] = [
    'Neckx',
    'NeckW',
    'NeckW2',
]
bone_reweight['Head'] = [
    'Neckx2',
]
bone_reweight['Eye_\L'] = [
    'EyeReturn_\L',
    'EyeW_\L',
]
bone_reweight['\Left shoulder'] = [
    'ShoulderC_\L',
    'Shoulder2_\L',
    'ShoulderSleeve_\L',
    'SleeveShoulderIK_\L',
    '\Left Shoulder Weight',
    'ShoulderS_\L',
    'ShoulderW_\L',
]
bone_reweight['\Left arm'] = [
    'ArmTwist_\L',
    'ArmTwist0_\L',
    'ArmTwist1_\L',
    'ArmTwist2_\L',
    'ArmTwist3_\L',
    'ArmTwist4_\L',
    '\Left Arm Twist',
    '\Left Arm Torsion',
    '\Left Arm Torsion 1',
    '\Left Arm Tight',
    '\Left Arm Tight 1',
    '\Left Arm Tight 2',
    '\Left Arm Tight 3',
    'ElbowAux_\L',
    'ElbowAux+_\L',
    '+ElbowAux_\L',
    'ArmSleeve_\L',
    'ShoulderTwist_\L',
    'ArmW_\L',
    'ArmW2_\L',
    '袖腕_\L',
    'SleeveArm_\L',
    '袖ひじ補助_\L',
    'SleeveElbowAux_\L',
    'DEF-upper_arm_02_\L',
    'DEF-upper_arm_twist_25_\L',
    'DEF-upper_arm_twist_50_\L',
    'DEF-upper_arm_twist_75_\L',
]
bone_reweight['Left arm'] = [  # This has apparently no side in the name
    'エプロンArm',
]
bone_reweight['\Left elbow'] = [
    'Elbow1_\L',
    'Elbow2_\L',
    'Elbow3_\L',
    'HandTwist_\L',
    'HandTwist1_\L',
    'HandTwist2_\L',
    'HandTwist3_\L',
    'HandTwist4_\L',
    '\Left Hand 1',
    '\Left Hand 2',
    '\Left Hand 3',
    '\Left Hand Twist',
    '\Left Hand Twist 1',
    '\Left Hand Twist 2',
    '\Left Hand Thread 3',
    'ElbowSleeve_\L',
    'WristAux_\L',
    'ElbowTwist_\L',
    'ElbowTwist2_\L',
    'ElbowW_\L',
    'ElbowW2_\L',
    '袖ひじ_\L',
    'SleeveElbow_\L',
    'Sleeve口_\L',
    'SleeveMouth_\L',
    'DEF-upper_arm_elbow_\L',
    'DEF-forearm_twist_25_\L',
    'DEF-forearm_twist_50_\L',
    'DEF-forearm_twist_75_\L',
    '+Elbow_\L',
    'Elbowa_\L',
]
bone_reweight['\Left wrist'] = [
    'WristSleeve_\L',
    'WristW_\L',
    'WristS_\L',
    'HandTwist5_\L',
    'IndexFinger0_\L',
    'MiddleFinger0_\L',
    'RingFinger0_\L',
    'LittleFinger0_\L',
    'DEF-hand_\L',
    'DEF-palm_01_\L',
    'DEF-palm_02_\L',
    'DEF-thumb_01_\L_01',
    'DEF-thumb_01_\L_02',
]
bone_reweight['\Left leg'] = [
    'LegD_\L',
    '\Left Foot D',
    '\Left Foot Complement',
    '\Left Foot Supplement',
    'Legcnt連_\L',
    '\L腿Twist1',
    '\L腿Twist2',
    '\L腿Twist3',
    'LegcntEven_\L',
    '\LLegTwist1',
    '\LLegTwist2',
    '\LLegTwist3',
    'LegW_\L',
    'LegW2_\L',
    'LowerKnee_\L',
    'UpperKnee_\L',
    'LegX1_\L',
    'LegX2_\L',
    'LegX3_\L',
    '\Left Knee EX',
    '\Left Foot EX',
    'KneeEX_\L',
    'LegEX_\L',
]
bone_reweight['\Left knee'] = [
    'KneeD_\L',
    '\Left Knee D',
    'Kneecnt連_\L',
    '\L脛Twist1',
    '\L脛Twist2',
    '\L脛Twist3',
    'KneecntEven_\L',
    '\LTibiaTwist1',
    '\LTibiaTwist2',
    '\LTibiaTwist3',
    'KneeW1_\L',
    'KneeW2_\L',
    'Knee+_\L',
    'KneeArmor2_\L',
    'KneeX1_\L',
    'KneeX2_\L',
    'KneeX3_\L',
    'Leg \Left Acc',
    '\Left Ankle EX',
    'AnkleEX_\L',
]
bone_reweight['\Left ankle'] = [
    'AnkleD_\L',
    '\Left Ankle D',
    'Ankle連_\L',
    'AnkleEven_\L',
    'AnkleW1_\L',
    'AnkleW2_\L',
    'Ankle+_\L',
    'ToeTipMovable_\L',
    'AnkleArmor_\L',
]
bone_reweight['\Left toe'] = [
    '爪TipEX_\L',
    '爪TipEX2_\L',
    '爪TipThumbEX_\L',
    '爪TipThumbEX2_\L',
    'ClawTipEX_\L',
    'ClawTipEX2_\L',
    'ClawTipThumbEX_\L',
    'ClawTipThumbEX2_\L',
]

# Old reweight list. Still important
bone_list_weight = {
    'DEF-palm_01_L': 'IndexFinger0_L',
    'DEF-palm_02_L': 'MiddleFinger0_L',
    'DEF-palm_03_L': 'RingFinger0_L',
    'DEF-palm_04_L': 'LittleFinger0_L',

    'DEF-f_Ling_01_L_02': 'RingFinger1_L',
    'DEF-f_Ling_01_L_01': 'RingFinger1_L',
    'DEF-f_Ling_02_L': 'RingFinger2_L',
    'DEF-f_Ling_03_L': 'RingFinger3_L',
    'DEF-f_middle_01_L_01': 'MiddleFinger1_L',
    'DEF-f_middle_01_L_02': 'MiddleFinger1_L',
    'DEF-f_middle_02_L': 'MiddleFinger2_L',
    'DEF-f_middle_03_L': 'MiddleFinger3_L',

    'DEF-f_index_03_L': 'IndexFinger3_L',
    'DEF-f_index_02_L': 'IndexFinger2_L',
    'DEF-f_index_01_L_02': 'IndexFinger1_L',
    'DEF-f_index_01_L_01': 'IndexFinger1_L',

    'DEF-f_pinky_03_L': 'LittleFinger3_L',
    'DEF-f_pinky_02_L': 'LittleFinger2_L',
    'DEF-f_pinky_01_L_02': 'LittleFinger1_L',
    'DEF-f_pinky_01_L_01': 'LittleFinger1_L',

    'DEF-thumb_01_L_01': 'Thumb0_L',
    'DEF-thumb_01_L_02': 'Thumb0_L',
    'DEF-thumb_02_L': 'Thumb1_L',
    'DEF-thumb_03_L': 'Thumb2_L',

    # Some weird model exception here
    'DEF-palm_01_R': 'IndexFinger0_R',
    'DEF-palm_02_R': 'MiddleFinger0_R',
    'DEF-palm_03_R': 'RingFinger0_R',
    'DEF-palm_04_R': 'LittleFinger0_R',

    'DEF-f_ring_01_R_02': 'RingFinger1_R',
    'DEF-f_ring_01_R_01': 'RingFinger1_R',
    'DEF-f_ring_02_R': 'RingFinger2_R',
    'DEF-f_ring_03_R': 'RingFinger3_R',
    'DEF-f_middle_01_R_01': 'MiddleFinger1_R',
    'DEF-f_middle_01_R_02': 'MiddleFinger1_R',
    'DEF-f_middle_02_R': 'MiddleFinger2_R',
    'DEF-f_middle_03_R': 'MiddleFinger3_R',

    'DEF-f_index_03_R': 'IndexFinger3_R',
    'DEF-f_index_02_R': 'IndexFinger2_R',
    'DEF-f_index_01_R_02': 'IndexFinger1_R',
    'DEF-f_index_01_R_01': 'IndexFinger1_R',

    'DEF-f_pinky_03_R': 'LittleFinger3_R',
    'DEF-f_pinky_02_R': 'LittleFinger2_R',
    'DEF-f_pinky_01_R_02': 'LittleFinger1_R',
    'DEF-f_pinky_01_R_01': 'LittleFinger1_R',

    'DEF-thumb_01_R_01': 'Thumb0_R',
    'DEF-thumb_01_R_02': 'Thumb0_R',
    'DEF-thumb_02_R': 'Thumb1_R',
    'DEF-thumb_03_R': 'Thumb2_R',
}
