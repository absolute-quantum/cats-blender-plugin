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
    'OldRightEye', 'OldLeftEye', 'LeftEye', 'RightEye', 'Eye_L', 'Eye_R'
}
bone_list_rename_unknown_side = {
    'Shoulder': 'shoulder',
    'Shoulder_001': 'shoulder'
}

############################
# Replace Old Bone Patterns:
#   Left/Right = \Left
#   L/R = \L
# Replace New Bone Patterns:
#   Left/Right = \Left
#   left/right = \left
#   L/R = \L
#   l/r = \l
############################
bone_rename = OrderedDict()
bone_rename['Hips'] = [
    'LowerBody',
    'Lowerbody',
    'Lower body',
    'Lower Body',
    'Mixamorig:Hips',
]
bone_rename['Spine'] = [
    'UpperBody',
    'Upperbody',
    'Upper body',
    'Upper Body',
    'Upper waist',
    'Upper Waist',
    'Mixamorig:Spine',
]
bone_rename['Chest'] = [
    'UpperBody2',
    'Upperbody2',
    'Upper body 2',
    'Upper Body 2',
    'Upper waist 2',
    'Upper Waist 2',
    'Waist upper 2',
    'Waist Upper 2',
    'Mixamorig:Spine1',
]
bone_rename['NewChest'] = [  # Will get deleted
    'UpperBody3',
    'Upperbody3',
    'Upper body 3',
    'Upper Body 3',
    'Upper waist 3',
    'Upper Waist 3',
    'Waist upper 3',
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
    'LegTipEX_\L',
    'ClawTipEX_\L',
    'Mixamorig:\LeftToeBase',
]
bone_rename['Eye_\L'] = [
    'Mixamorig:\LeftEye',
]

######################
######################
bone_list_weight = {
    'LowerBody1': 'Hips',
    'LowerBody2': 'Hips',

    'UpperBodyx': 'Spine',
    'UpperBodyx2': 'Chest',

    'Neckx': 'Neck',
    'NeckW': 'Neck',
    'NeckW2': 'Neck',

    'Neckx2': 'Head',

    'EyeReturn_L': 'Eye_L',
    'EyeW_L': 'Eye_L',

    'EyeReturn_R': 'Eye_R',
    'EyeW_R': 'Eye_R',

    'LegD_L': 'Left leg',
    'Left foot D': 'Left leg',
    'Left foot complement': 'Left leg',
    'Left foot supplement': 'Left leg',
    'Legcnt連_L': 'Left leg',
    'L腿Twist1': 'Left leg',
    'L腿Twist2': 'Left leg',
    'L腿Twist3': 'Left leg',
    'LegcntEven_L': 'Left leg',
    'LLegTwist1': 'Left leg',
    'LLegTwist2': 'Left leg',
    'LLegTwist3': 'Left leg',
    'LegW_L': 'Left leg',
    'LegW2_L': 'Left leg',
    'LowerKnee_L': 'Left leg',
    'UpperKnee_L': 'Left leg',

    'LegD_R': 'Right leg',
    'Right foot D': 'Right leg',
    'Right foot complement': 'Right leg',
    'Right foot supplement': 'Right leg',
    'Legcnt連_R': 'Right leg',
    'R腿Twist1': 'Right leg',
    'R腿Twist2': 'Right leg',
    'R腿Twist3': 'Right leg',
    'LegcntEven_R': 'Right leg',
    'RLegTwist1': 'Right leg',
    'RLegTwist2': 'Right leg',
    'RLegTwist3': 'Right leg',
    'LegW_R': 'Right leg',
    'LegW2_R': 'Right leg',
    'KneeS_R': 'Right leg',
    'LowerKnee_R': 'Right leg',
    'UpperKnee_R': 'Right leg',

    'KneeD_L': 'Left knee',
    'Left knee D': 'Left knee',
    'Kneecnt連_L': 'Left knee',
    'L脛Twist1': 'Left knee',
    'L脛Twist2': 'Left knee',
    'L脛Twist3': 'Left knee',
    'KneecntEven_L': 'Left knee',
    'LTibiaTwist1': 'Left knee',
    'LTibiaTwist2': 'Left knee',
    'LTibiaTwist3': 'Left knee',
    'KneeW1_L': 'Left knee',
    'KneeW2_L': 'Left knee',
    'Knee+_L': 'Left knee',
    'KneeArmor2_L': 'Left knee',

    'KneeD_R': 'Right knee',
    'Right knee D': 'Right knee',
    'Kneecnt連_R': 'Right knee',
    'R脛Twist1': 'Right knee',
    'R脛Twist2': 'Right knee',
    'R脛Twist3': 'Right knee',
    'KneecntEven_R': 'Right knee',
    'RTibiaTwist1': 'Right knee',
    'RTibiaTwist2': 'Right knee',
    'RTibiaTwist3': 'Right knee',
    'KneeW1_R': 'Right knee',
    'KneeW2_R': 'Right knee',
    'Knee+_R': 'Right knee',
    'KneeArmor2_R': 'Right knee',

    'AnkleD_L': 'Left ankle',
    'Left ankle D': 'Left ankle',
    'Ankle連_L': 'Left ankle',
    'AnkleEven_L': 'Left ankle',
    'AnkleW1_L': 'Left ankle',
    'AnkleW2_L': 'Left ankle',
    'Ankle+_L': 'Left ankle',
    'ToeTipMovable_L': 'Left ankle',
    'AnkleArmor_L': 'Left ankle',

    'AnkleD_R': 'Right ankle',
    'Right ankle D': 'Right ankle',
    'Ankle連_R': 'Right ankle',
    'AnkleEven_R': 'Right ankle',
    'AnkleW1_R': 'Right ankle',
    'AnkleW2_R': 'Right ankle',
    'Ankle+_R': 'Right ankle',
    'ToeTipMovable_R': 'Right ankle',
    'AnkleArmor_R': 'Right ankle',

    '爪TipEX_L': 'Left toe',
    '爪TipEX2_L': 'Left toe',
    '爪TipThumbEX_L': 'Left toe',
    '爪TipThumbEX2_L': 'Left toe',
    'ClawTipEX_L': 'Left toe',
    'ClawTipEX2_L': 'Left toe',
    'ClawTipThumbEX_L': 'Left toe',
    'ClawTipThumbEX2_L': 'Left toe',

    '爪TipEX_R': 'Right toe',
    '爪TipEX2_R': 'Right toe',
    '爪TipThumbEX_R': 'Right toe',
    '爪TipThumbEX2_R': 'Right toe',
    'ClawTipEX_R': 'Right toe',
    'ClawTipEX2_R': 'Right toe',
    'ClawTipThumbEX_R': 'Right toe',
    'ClawTipThumbEX2_R': 'Right toe',

    'ShoulderC_R': 'Right shoulder',
    'Shoulder2_R': 'Right shoulder',
    'ShoulderSleeve_R': 'Right shoulder',
    'SleeveShoulderIK_R': 'Right shoulder',
    'Right shoulder weight': 'Right shoulder',
    'ShoulderS_R': 'Right shoulder',
    'ShoulderW_R': 'Right shoulder',

    'ShoulderC_L': 'Left shoulder',
    'Shoulder2_L': 'Left shoulder',
    'ShoulderSleeve_L': 'Left shoulder',
    'SleeveShoulderIK_L': 'Left shoulder',
    'Left shoulder weight': 'Left shoulder',
    'ShoulderS_L': 'Left shoulder',
    'ShoulderW_L': 'Left shoulder',

    'ArmTwist_R': 'Right arm',
    'ArmTwist1_R': 'Right arm',
    'ArmTwist2_R': 'Right arm',
    'ArmTwist3_R': 'Right arm',
    'ArmTwist4_R': 'Right arm',
    'Right arm twist': 'Right arm',
    'Right arm torsion': 'Right arm',
    'Right arm torsion 1': 'Right arm',
    'Right arm tight': 'Right arm',
    'Right arm tight 1': 'Right arm',
    'Right arm tight 2': 'Right arm',
    'Right arm tight 3': 'Right arm',
    'ElbowAux_R': 'Right arm',
    'ElbowAux+_R': 'Right arm',
    '+ElbowAux_R': 'Right arm',
    'ArmSleeve_R': 'Right arm',
    'ShoulderTwist_R': 'Right arm',
    'ArmW_R': 'Right arm',
    'ArmW2_R': 'Right arm',
    '袖腕.R': 'Right arm',
    'SleeveArm_R': 'Right arm',
    '袖ひじ補助.R': 'Right arm',
    'SleeveElbowAux_R': 'Right arm',
    'DEF-upper_arm_02_R': 'Right arm',
    'DEF-upper_arm_twist_25_R': 'Right arm',
    'DEF-upper_arm_twist_50_R': 'Right arm',
    'DEF-upper_arm_twist_75_R': 'Right arm',

    'ArmTwist_L': 'Left arm',
    'ArmTwist1_L': 'Left arm',
    'ArmTwist2_L': 'Left arm',
    'ArmTwist3_L': 'Left arm',
    'ArmTwist4_L': 'Left arm',
    'Left arm twist': 'Left arm',
    'Left arm torsion': 'Left arm',
    'Left arm torsion 1': 'Left arm',
    'Left arm tight': 'Left arm',
    'Left arm tight 1': 'Left arm',
    'Left arm tight 2': 'Left arm',
    'Left arm tight 3': 'Left arm',
    'ElbowAux_L': 'Left arm',
    'ElbowAux+_L': 'Left arm',
    '+ElbowAux_L': 'Left arm',
    'ArmSleeve_L': 'Left arm',
    'ShoulderTwist_L': 'Left arm',
    'ArmW_L': 'Left arm',
    'ArmW2_L': 'Left arm',
    'エプロンArm': 'Left arm',
    'SleeveArm_L': 'Left arm',
    '袖ひじ補助.L': 'Left arm',
    'SleeveElbowAux_L': 'Left arm',
    'DEF-upper_arm_02_L': 'Left arm',
    'DEF-upper_arm_twist_25_L': 'Left arm',
    'DEF-upper_arm_twist_50_L': 'Left arm',
    'DEF-upper_arm_twist_75_L': 'Left arm',

    'Elbow1_R': 'Right elbow',
    'Elbow2_R': 'Right elbow',
    'Elbow3_R': 'Right elbow',
    'HandTwist_R': 'Right elbow',
    'HandTwist1_R': 'Right elbow',
    'HandTwist2_R': 'Right elbow',
    'HandTwist3_R': 'Right elbow',
    'HandTwist4_R': 'Right elbow',
    'Right Hand 1': 'Right elbow',
    'Right Hand 2': 'Right elbow',
    'Right Hand 3': 'Right elbow',
    'Right hand 1': 'Right elbow',
    'Right hand 2': 'Right elbow',
    'Right hand 3': 'Right elbow',
    'Right hand twist': 'Right elbow',
    'Right hand twist 1': 'Right elbow',
    'Right hand twist 2': 'Right elbow',
    'Right Hand Thread 3': 'Right elbow',
    'ElbowSleeve_R': 'Right elbow',
    'WristAux_R': 'Right elbow',
    'ElbowTwist_R': 'Right elbow',
    'ElbowTwist2_R': 'Right elbow',
    'ElbowW_R': 'Right elbow',
    'ElbowW2_R': 'Right elbow',
    '袖ひじ.R': 'Right elbow',
    'SleeveElbow_R': 'Right elbow',
    'Sleeve口_R': 'Right elbow',
    'SleeveMouth_R': 'Right elbow',
    'DEF-upper_arm_elbow_R': 'Right elbow',
    'DEF-forearm_twist_75_R': 'Right elbow',
    'DEF-forearm_twist_50_R': 'Right elbow',
    'DEF-forearm_twist_25_R': 'Right elbow',
    '+Elbow_R': 'Right elbow',

    'Elbow1_L': 'Left elbow',
    'Elbow2_L': 'Left elbow',
    'Elbow3_L': 'Left elbow',
    'HandTwist_L': 'Left elbow',
    'HandTwist1_L': 'Left elbow',
    'HandTwist2_L': 'Left elbow',
    'HandTwist3_L': 'Left elbow',
    'HandTwist4_L': 'Left elbow',
    'Left Hand 1': 'Left elbow',
    'Left Hand 2': 'Left elbow',
    'Left Hand 3': 'Left elbow',
    'Left hand 1': 'Left elbow',
    'Left hand 2': 'Left elbow',
    'Left hand 3': 'Left elbow',
    'Left hand twist': 'Left elbow',
    'Left hand twist 1': 'Left elbow',
    'Left hand twist 2': 'Left elbow',
    'Left Hand Thread 3': 'Left elbow',
    'ElbowSleeve_L': 'Left elbow',
    'WristAux_L': 'Left elbow',
    'ElbowTwist_L': 'Left elbow',
    'ElbowTwist2_L': 'Left elbow',
    'ElbowW_L': 'Left elbow',
    'ElbowW2_L': 'Left elbow',
    '袖ひじ.L': 'Left elbow',
    'SleeveElbow_L': 'Left elbow',
    'Sleeve口_L': 'Left elbow',
    'SleeveMouth_L': 'Left elbow',
    'DEF-upper_arm_elbow_L': 'Left elbow',
    'DEF-forearm_twist_75_L': 'Left elbow',
    'DEF-forearm_twist_50_L': 'Left elbow',
    'DEF-forearm_twist_25_L': 'Left elbow',
    '+Elbow_L': 'Left elbow',

    'WristSleeve_L': 'Left wrist',
    'WristW_L': 'Left wrist',
    'WristS_L': 'Left wrist',
    'HandTwist5_L': 'Left wrist',

    'WristSleeve_R': 'Right wrist',
    'WristW_R': 'Right wrist',
    'WristS_R': 'Right wrist',
    'HandTwist5_R': 'Right wrist',

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

    'Thumb0_R': 'Right wrist',
    'IndexFinger0_R': 'Right wrist',
    'MiddleFinger0_R': 'Right wrist',
    'RingFinger0_R': 'Right wrist',
    'LittleFinger0_R': 'Right wrist',

    'DEF-thumb_01_R_02': 'Right wrist',
    'DEF-hand_R': 'Right wrist',
    'DEF-thumb_01_R_01': 'Right wrist',
    'DEF-palm_01_R': 'Right wrist',
    'DEF-palm_02_R': 'Right wrist',

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

    'Thumb0_L': 'Left wrist',
    'IndexFinger0_L': 'Left wrist',
    'MiddleFinger0_L': 'Left wrist',
    'RingFinger0_L': 'Left wrist',
    'LittleFinger0_L': 'Left wrist',

    'DEF-thumb_01_L_02': 'Left wrist',
    'DEF-hand_L': 'Left wrist',
    'DEF-thumb_01_L_01': 'Left wrist',
    'DEF-palm_01_L': 'Left wrist',
    'DEF-palm_02_L': 'Left wrist',
}