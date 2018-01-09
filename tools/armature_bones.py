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
    'Right toe': 'Right ankle',

    'Thumb0_L': 'Left wrist',
    'IndexFinger1_L': 'Left wrist',
    'MiddleFinger1_L': 'Left wrist',
    'RingFinger1_L': 'Left wrist',
    'LittleFinger1_L': 'Left wrist',

    'Thumb1_L': 'Thumb0_L',
    'IndexFinger2_L': 'IndexFinger1_L',
    'MiddleFinger2_L': 'MiddleFinger1_L',
    'RingFinger2_L': 'RingFinger1_L',
    'LittleFinger2_L': 'LittleFinger1_L',

    'Thumb2_L': 'Thumb1_L',
    'IndexFinger3_L': 'IndexFinger2_L',
    'MiddleFinger3_L': 'MiddleFinger2_L',
    'RingFinger3_L': 'RingFinger2_L',
    'LittleFinger3_L': 'LittleFinger2_L',

    'Thumb0_R': 'Right wrist',
    'IndexFinger1_R': 'Right wrist',
    'MiddleFinger1_R': 'Right wrist',
    'RingFinger1_R': 'Right wrist',
    'LittleFinger1_R': 'Right wrist',

    'Thumb1_R': 'Thumb0_R',
    'IndexFinger2_R': 'IndexFinger1_R',
    'MiddleFinger2_R': 'MiddleFinger1_R',
    'RingFinger2_R': 'RingFinger1_R',
    'LittleFinger2_R': 'LittleFinger1_R',

    'Thumb2_R': 'Thumb1_R',
    'IndexFinger3_R': 'IndexFinger2_R',
    'MiddleFinger3_R': 'MiddleFinger2_R',
    'RingFinger3_R': 'RingFinger2_R',
    'LittleFinger3_R': 'LittleFinger2_R',

    # Special cases
    'M_head_copy': 'Head',
}
dont_delete_these_bones = {
    'Hips', 'Spine', 'Chest', 'Neck', 'Head',
    'Left leg', 'Left knee', 'Left ankle', 'Left toe',
    'Right leg', 'Right knee', 'Right ankle', 'Right toe',
    'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist',
    'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist',
    'OldRightEye', 'OldLeftEye', 'LeftEye', 'RightEye', 'Eye_L', 'Eye_R',

    'Thumb0_L', 'Thumb1_L', 'Thumb2_L',
    'IndexFinger1_L', 'IndexFinger2_L', 'IndexFinger3_L',
    'MiddleFinger1_L', 'MiddleFinger2_L', 'MiddleFinger3_L',
    'RingFinger1_L', 'RingFinger2_L', 'RingFinger3_L',
    'LittleFinger1_L', 'LittleFinger2_L', 'LittleFinger3_L',

    'Thumb0_R', 'Thumb1_R', 'Thumb2_R',
    'IndexFinger1_R', 'IndexFinger2_R', 'IndexFinger3_R',
    'MiddleFinger1_R', 'MiddleFinger2_R', 'MiddleFinger3_R',
    'RingFinger1_R', 'RingFinger2_R', 'RingFinger3_R',
    'LittleFinger1_R', 'LittleFinger2_R', 'LittleFinger3_R',

    'Breast_L', 'Breast_R',
}
bone_list_rename_unknown_side = {
    'Shoulder': 'shoulder',
    'Shoulder_001': 'shoulder'
}
bone_finger_list = [
    'Thumb0_',
    'IndexFinger1_',
    'MiddleFinger1_',
    'RingFinger1_',
    'LittleFinger1_',

    'Thumb1_',
    'IndexFinger2_',
    'MiddleFinger2_',
    'RingFinger2_',
    'LittleFinger2_',

    'Thumb2_',
    'IndexFinger3_',
    'MiddleFinger3_',
    'RingFinger3_',
    'LittleFinger3_',
]

################################
# Capitalize all bone names!
# Capitalize after each space!
# Replace '-' with '_'
# Replace 'ValveBiped_' with ''
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
    'Pelvis',
    'Bip001 Pelvis',
    'Bip01_Pelvis',
    'Root',
    'Root Hips',
    'Root_rot',
    'Hip',
]
bone_rename['Spine'] = [  # This is a list of all the spine and chest bones. They will be correctly fixed
    'Spine',  # First entry!

    # MMD
    'UpperBody',
    'Upperbody',
    'Upper Body',
    'Upper Waist',
    'UpperBody2',
    'Upperbody2',
    'Upper Body 2',
    'Upper Waist 2',
    'Waist Upper 2',
    'UpperBody3',
    'Upperbody3',
    'Upper Body 3',
    'Upper Waist 3',
    'Waist Upper 3',

    # Mixamo
    'Mixamorig:Spine',
    'Mixamorig:Spine0',
    'Mixamorig:Spine1',
    'Mixamorig:Spine2',
    'Mixamorig:Spine3',
    'Mixamorig:Spine4',

    # 3DMax?
    'Bip001 Spine',
    'Bip001 Spine0',
    'Bip001 Spine1',
    'Bip001 Spine2',
    'Bip001 Spine3',
    'Bip001 Spine4',
    'Bip001 Spine5',

    'Bip01_Spine',
    'Bip01_Spine1',
    'Bip01_Spine2',
    'Bip01_Spine3',
    'Bip01_Spine4',
    'Bip01_Spine5',

    # Something
    'B C Spine',
    'B C Spine0',
    'B C Spine1',
    'B C Spine2',
    'B C Spine3',
    'B C Spine4',
    'B C Spine5',
    'B C Chest',

    # .Mesh
    'Spine Lower',
    'Spine Upper',

    'abdomen',

    'Spine0',
    'Spine1',
    'Spine2',
    'Spine3',
    'Spine4',
    'Spine5',

    'Spine 0',
    'Spine 1',
    'Spine 2',
    'Spine 3',
    'Spine 4',
    'Spine 5',

    'Chest1',
    'Chest2',
    'Chest3',

    'Chest'  # Last entry!
]
bone_rename['Neck'] = [
    'Mixamorig:Neck',
    'Head Neck Lower',
    'Bip001 Neck',
    'Bip01_Neck',
    'B C Neck1',
]
bone_rename['Head'] = [
    'Mixamorig:Head',
    'Head Neck Upper',
    'Bip001 Head',
    'Bip01_Head',
    'B C Head',
]
bone_rename['\Left shoulder'] = [
    '\Left Shoulder',
    '\LeftShoulder',
    'Shoulder_\L',
    'Mixamorig:\LeftShoulder',
    'Arm \Left Shoulder 1',
    'Bip001 \L Clavicle',
    'Bip01_\L_Clavicle',
    'B \L Shoulder',
    'Shoulder \L',
    '\LCollar',
    '\L_clavicle',
    '\LeftCollar',
    '\Left Collar',
]
bone_rename['\Left arm'] = [
    '\Left Arm',
    '\LeftArm',
    'Arm_\L',
    'ArmTC_\L',
    '+ \Left Elbow Support',
    '+ \Left Elbow Support',
    'Mixamorig:\LeftArm',
    'Arm \Left Shoulder 2',
    'Bip001 \L UpperArm',
    'Bip01_\L_UpperArm',
    'B \L Arm1',
    'Upper Arm \L',
    '\LShldr',
    'Upper_arm_\L',
    '\L_upperarm',
    '\LeftUpArm',
    'Uparm_\L',
]
bone_rename['Left arm'] = [
    '+ Leisure Elder Supplement',
]
bone_rename['\Left elbow'] = [
    '\Left Elbow',
    '\LeftElbow',
    'Elbow_\L',
    'Mixamorig:\LeftForeArm',
    'Arm \Left Elbow',
    'Bip001 \L Forearm',
    'Bip01_\L_Forearm',
    'B \L Arm2',
    'Forearm \L',
    '\LForeArm',
    'forearm_\L',
    '\L_forearm',
    '\LeftLowArm',
    '\Left Forearm',
    'Loarm_\L',
]
bone_rename['\Left wrist'] = [
    '\Left Wrist',
    '\LeftWrist',
    'Wrist_\L',
    'HandAux2_\L',
    'Mixamorig:\LeftHand',
    'Arm \Left Wrist',
    'Bip001 \L Hand',
    'Bip01_\L_Hand',
    'B \L Hand',
    'Hand \L',
    '\LHand',
    'Hand_\L',
    '\L_hand',
    '\LeftHand',
    '\Left Hand',
    'Finger3_1_\L'
]
bone_rename['\Left leg'] = [
    '\Left Leg',
    '\Left foot',
    '\LeftLeg',
    'Leg_\L',
    'LegWAux_\L',
    'Leg00003333_\L',
    'Leg00004444_\L',
    'Mixamorig:\LeftUpLeg',
    'Leg \Left Thigh',
    'Bip001 \L Thigh',
    'Bip01_\L_Thigh',
    'B \L Leg1',
    'Upper Leg \L',
    '\LThigh',
    'Thigh_\L',
    '\L_thigh',
    '\LeftUpLeg',
    '\LeftHip',
    '\Left Thigh',
    'Upleg_\L'
]
bone_rename['\Left knee'] = [
    '\Left Knee',
    '\LeftKnee',
    'Knee_\L',
    'Mixamorig:\LeftLeg',
    'Leg \Left Knee',
    'Bip001 \L Calf',
    'Bip01_\L_Calf',
    'B \L Leg2',
    'Lower Leg \L',
    '\LShin',
    'Shin_\L',
    '\L_calf',
    '\LeftLowLeg',
    '\Left Shin',
    'Loleg_\L'
]
bone_rename['\Left ankle'] = [
    '\Left Ankle',
    '\LeftAnkle',
    'Ankle_\L',
    'Mixamorig:\LeftFoot',
    'Leg \Left Ankle',
    'Bip001 \L Foot',
    'Bip01_\L_Foot',
    'B \L Foot',
    'Lower',
    '\LFoot',
    'Foot_\L',
    '\L_foot',
    '\LeftFoot',
    '\Left Foot',
    'Leg \Left Foot',
]
bone_rename['\Left toe'] = [
    '\Left Toe',
    '\LeftToe',
    'LegTip_\L',
    'LegTipEX_\L',
    'ClawTipEX_\L',
    'Mixamorig:\LeftToeBase',
    'Leg \Left Toes',
    'Bip001 \L Toe0',
    'Bip01_\L_Toe0',
    'B \L Toe',
    '\LToe',
    'Toe_\L',
    '\L_toe',
    '\LeftToeBase',
    'Toe1_1_\L',
    'Leg \Left Foot Toes',
]
bone_rename['Eye_\L'] = [
    '\Left Eye',
    'Mixamorig:\LeftEye',
    'Head Eyeball \Left',
    'FEye\L',
    'Eye\L',
    '\L_eye',
]

################################
# Capitalize all bone names!
# Capitalize after each space!
# Replace '-' with '_'
# Replace 'ValveBiped_' with ''
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
    'Pelvis Adj',
]
bone_reweight['Spine'] = [
    'UpperBodyx',
    'Spine Lower Adj',
    'Spine Middle Adj',
]
bone_reweight['Chest'] = [
    'UpperBodyx2',
    'Spine Upper Adj',
]
bone_reweight['Neck'] = [
    'Neckx',
    'NeckW',
    'NeckW2',
]
bone_reweight['Head'] = [
    'Neckx2',
]
bone_reweight['\Left shoulder'] = [
    'ShoulderC_\L',
    'ShoulderP_\L',
    'Shoulder2_\L',
    'ShoulderSleeve_\L',
    'SleeveShoulderIK_\L',
    '\Left Shoulder Weight',
    'ShoulderS_\L',
    'ShoulderW_\L',
    'Arm \Left Shoulder Adj 1',
    'B \L ArmorParts',
]
bone_reweight['\Left arm'] = [
    'Arm01_\L',
    'Arm02_\L',
    'Arm03_\L',
    'Arm04_\L',
    'Arm05_\L',
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
    'Sleeve1_\L',
    'SleeveArm_\L',
    'SleeveElbowAux_\L',
    'ArmxcIa_\L',
    'ArmRotation_\L',
    'ArmTwistReturn_\L',
    'DEF_upper_arm_02_\L',
    'DEF_upper_arm_twist_25_\L',
    'DEF_upper_arm_twist_50_\L',
    'DEF_upper_arm_twist_75_\L',
    'Arm \Left Shoulder Adj 2',
    'Arm \Left Shoulder Adj 3',
    'Arm \Left Shoulder Adj 4',
    'Arm \Left Bicep',
]
bone_reweight['Left arm'] = [  # This has apparently no side in the name
    'エプロンArm',
]
bone_reweight['\Left elbow'] = [
    'Elbow1_\L',
    'Elbow2_\L',
    'Elbow3_\L',
    'Elbow01_\L',
    'Elbow02_\L',
    'Elbow03_\L',
    'Elbow04_\L',
    'Elbow05_\L',
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
    'Sleeve2_\L',
    'SleeveElbow_\L',
    'SleeveMouth_\L',
    'ElbowRotation_\L',
    'HandTwistRotation1_\L',
    'HandTwistRotation2_\L',
    'DEF_upper_arm_elbow_\L',
    'DEF_forearm_twist_25_\L',
    'DEF_forearm_twist_50_\L',
    'DEF_forearm_twist_75_\L',
    '+Elbow_\L',
    'Elbowa_\L',
    'Arm \Left Wrist Adj',
    'Arm \Left Elbow Adj 2',
    'Arm \Left Elbow Adj 1',
    'Arm \Left Forearm'
]
bone_reweight['\Left wrist'] = [
    'Sleeve3_\L',
    'WristSleeve_\L',
    'WristW_\L',
    'WristS_\L',
    'HandTwist5_\L',
    'IndexFinger0_\L',
    'MiddleFinger0_\L',
    'RingFinger0_\L',
    'LittleFinger0_\L',
    'DEF_hand_\L',
    'DEF_palm_01_\L',
    'DEF_palm_02_\L',
    'DEF_palm_03_\L',
    'DEF_palm_04_\L',
    'Arm \Left Hand',
]
bone_reweight['\Left leg'] = [
    'LegD_\L',
    '+LegD_\L',
    '\Left Foot D',
    '\Left Foot Complement',
    '\Left Foot Supplement',
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
    'Thigh_\L',
    'Leg+_\L',
    'Leg++_\L',
    'Leg+++_\L',
    'Leg++++_\L',
    'Knee++_\L',
    'Peaches_\L',
    'Pants_Stuff_000_\L',
    'Pants_Stuff_001_\L',
    'DEF_thigh_sub_\L',
    'DEF_thigh_01_\L',
    'DEF_thigh_02_\L',
    'DEF_thigh_twist_25_\L',
    'DEF_thigh_twist_50_\L',
    'DEF_thigh_twist_75_\L',
    'Leg \Left Thigh Adj 1',
    'Leg \Left Thigh Adj 2',
    'Leg \Left Thigh Adj 3',
]
bone_reweight['\Left knee'] = [
    'KneeD_\L',
    '\Left Knee D',
    'KneecntEven_\L',
    '\LTibiaTwist1',
    '\LTibiaTwist2',
    '\LTibiaTwist3',
    'KneeW1_\L',
    'KneeW2_\L',
    'Knee+_\L',
    'Knee+++_\L',
    'Knee++++_\L',
    'Ankle++_\L',
    'KneeArmor2_\L',
    'KneeX1_\L',
    'KneeX2_\L',
    'KneeX3_\L',
    'Leg \Left Acc',
    '\Left Ankle EX',
    'AnkleEX_\L',
    'KneeAux_\L',
    'Shin_\L',
    'DEF_knee_\L',
    'DEF_knee_02_\L',
    'DEF_shin_01_\L',
    'DEF_shin_02_\L',
    'DEF_shin_twist_25_\L',
    'DEF_shin_twist_50_\L',
    'DEF_shin_twist_75_\L',
    'Leg \Left Ankle Adj',
    'Leg \Left Knee Adj 1',
    'Leg \Left Knee Adj 2',
]
bone_reweight['\Left ankle'] = [
    'AnkleD_\L',
    '\Left Ankle D',
    'AnkleEven_\L',
    'AnkleW1_\L',
    'AnkleW2_\L',
    'ToeTipMovable_\L',
    'AnkleArmor_\L',
    'LowerUseless_\L',
    'Ankle+_\L',
    'Ankle+++_\L',
    'Ankle++++_\L',
    'DEF_foot_\L',
]
bone_reweight['\Left toe'] = [
    'ClawTipEX_\L',
    'ClawTipEX2_\L',
    'ClawTipThumbEX_\L',
    'ClawTipThumbEX2_\L',
    '\Left Toe EX',
    '\Left Foot Tip EX',
    'LegTip2_\L',
    'DEF_toe_\L',
]
bone_reweight['Eye_\L'] = [
    'EyeW_\L',
    'EyeLight_\L',
    'EyeReturn_\L',
    'Pupil_\L',
    'Highlight_\L',
    'F_EyeTip_\L',
    'F_EyeLight1_\L',
    'F_EyeLight2_\L',
    'F_EyeLight3_\L',
    'DEF_eye_\L',
    'EyeLight+_\L',
    'EyeRotationErase_\L',
]
bone_reweight['Breast_\L'] = [
    'DEF_bust_01_\L',
    'DEF_bust_02_\L',
]

# Secondary reweight list.
bone_list_weight = {
    # Other model fixes
    'DEF_zipper': 'Zipper',

    # Finger fixing
    # Left
    'DEF_thumb_01_L_01': 'Thumb0_L',
    'DEF_thumb_01_L_02': 'Thumb0_L',
    'DEF_thumb_02_L': 'Thumb1_L',
    'DEF_thumb_03_L': 'Thumb2_L',

    'DEF_f_index_01_L_01': 'IndexFinger1_L',
    'DEF_f_index_01_L_02': 'IndexFinger1_L',
    'DEF_f_index_02_L': 'IndexFinger2_L',
    'DEF_f_index_03_L': 'IndexFinger3_L',

    'DEF_f_middle_01_L_01': 'MiddleFinger1_L',
    'DEF_f_middle_01_L_02': 'MiddleFinger1_L',
    'DEF_f_middle_02_L': 'MiddleFinger2_L',
    'DEF_f_middle_03_L': 'MiddleFinger3_L',

    'DEF_f_ring_01_L_01': 'RingFinger1_L',
    'DEF_f_ring_01_L_02': 'RingFinger1_L',
    'DEF_f_ring_02_L': 'RingFinger2_L',
    'DEF_f_ring_03_L': 'RingFinger3_L',

    'DEF_f_pinky_01_L_01': 'LittleFinger1_L',
    'DEF_f_pinky_01_L_02': 'LittleFinger1_L',
    'DEF_f_pinky_02_L': 'LittleFinger2_L',
    'DEF_f_pinky_03_L': 'LittleFinger3_L',

    # Right
    'DEF_thumb_01_R_01': 'Thumb0_R',
    'DEF_thumb_01_R_02': 'Thumb0_R',
    'DEF_thumb_02_R': 'Thumb1_R',
    'DEF_thumb_03_R': 'Thumb2_R',

    'DEF_f_index_01_R_01': 'IndexFinger1_R',
    'DEF_f_index_01_R_02': 'IndexFinger1_R',
    'DEF_f_index_02_R': 'IndexFinger2_R',
    'DEF_f_index_03_R': 'IndexFinger3_R',

    'DEF_f_middle_01_R_01': 'MiddleFinger1_R',
    'DEF_f_middle_01_R_02': 'MiddleFinger1_R',
    'DEF_f_middle_02_R': 'MiddleFinger2_R',
    'DEF_f_middle_03_R': 'MiddleFinger3_R',

    'DEF_f_ring_01_R_01': 'RingFinger1_R',
    'DEF_f_ring_01_R_02': 'RingFinger1_R',
    'DEF_f_ring_02_R': 'RingFinger2_R',
    'DEF_f_ring_03_R': 'RingFinger3_R',

    'DEF_f_pinky_01_R_01': 'LittleFinger1_R',
    'DEF_f_pinky_01_R_02': 'LittleFinger1_R',
    'DEF_f_pinky_02_R': 'LittleFinger2_R',
    'DEF_f_pinky_03_R': 'LittleFinger3_R',
}
