dictionary = {
    # Class.label / Class.desc (tooltip)
    # Class.property

    # Language name
    'name': 'ko_KR',

    # Main file
    'Main.error.restartAdmin': '\n\n잘못된 CATS 설치가 발견되었습니다!'
                               '\n이 문제를 해결하려면 Blender를 관리자로 다시 시작하세요!     '
                               '\n',
    'Main.error.deleteFollowing': '                                                                                                                                                                                    '
                                  '                     '
                                  '\n\n잘못된 CATS 설치가 발견되었습니다!'
                                  '\n이 문제를 해결하려면 addons 폴더에서 다음 파일과 폴더를 삭제하세요.:'
                                  '\n',
    'Main.error.installViaPreferences': '\n\n잘못된 CATS 설치 발견되었습니다!'
                                        '\n사용자 환경 설정(User Preferences)을 통해 CATS를 설치하고 블렌더를 다시 시작하세요!'
                                        '\n',
    'Main.error.restartAndEnable': '\n\n잘못된 CATS 설치가 발견되고 수정되었습니다!'
                                   '\nBlender를 다시 시작하고 CATS를 다시 활성화하세요!'
                                   '\n',
    'Main.error.unsupportedVersion': '\n\n2.79 이전의 블렌더 버전은 Cats에서 지원하지 않습니다. '
                                     '\nBlender 2.79 버전 이상을 사용하세요.'
                                     '\n',
    'Main.error.beta2.80': '\n\n아직 Blender 2.80 베타 버전을 사용 중입니다!'
                           '\nBlender를 2.80 정식 버전으로 업데이트하세요.'
                           '\n',
    'Main.error.restartAndEnable_alt': '\n\nBlender를 다시 시작하고 CATS를 다시 활성화하세요!'
                                       '\n',

    # UI Main
    'ToolPanel.label': 'Cats Blender Plugin',
    'ToolPanel.category': 'CATS',

    # UI Armature
    'ArmaturePanel.label': '모델',
    'ArmaturePanel.warn.oldBlender1': '이전 블렌더 버전이 발견되었습니다!',
    'ArmaturePanel.warn.oldBlender2': '일부 기능이 작동하지 않을 수 있습니다!',
    'ArmaturePanel.warn.oldBlender3': '블렌더 2.79 버전으로 업데이트하세요!',
    'ArmaturePanel.warn.noDict1': '사전파일(Dictionary)을 찾을 수 없습니다!',
    'ArmaturePanel.warn.noDict2': '번역은 되지만 최적화되지는 않습니다.',
    'ArmaturePanel.warn.noDict3': '이 문제를 해결하려면 Cats를 다시 설치하세요.',
    'ArmaturePanel.ImportAnyModel.label': '모델 불러오기',
    'ModelSettings.label': '모델 고치기 설정',
    'ModelSettings.warn.fbtFix1': '풀바디 트래킹 수정',
    'ModelSettings.warn.fbtFix2': 'VRChat에 더 이상 필요하지 않음.',
    'ModelSettings.warn.fbtFix3': '이것은 모델옵션에서 여전히 이용가능.',

    # UI Manual
    'ManualPanel.label': '모델 옵션',
    'ManualPanel.separateBy': '메쉬 분리:',
    'ManualPanel.SeparateByMaterials.label': '매테리얼별로',
    'ManualPanel.SeparateByLooseParts.label': '느슨한 부분별로',
    'ManualPanel.SeparateByShapekeys.label': '쉐이프별로',
    'ManualPanel.joinMeshes': '메쉬 통합:',
    'ManualPanel.JoinMeshes.label': '모두',
    'ManualPanel.JoinMeshesSelected.label': '선택된 메쉬들',
    'ManualPanel.mergeWeights': '웨이트 통합:',
    'ManualPanel.MergeWeights.label': '부모 본으로',
    'ManualPanel.MergeWeightsToActive.label': '활성화된 본으로',
    'ManualPanel.translate': '번역:',
    'ManualPanel.TranslateAllButton.label': '모두',
    'ManualPanel.TranslateShapekeyButton.label': '쉐이프키',
    'ManualPanel.TranslateObjectsButton.label': '오브젝트',
    'ManualPanel.TranslateBonesButton.label': '본',
    'ManualPanel.TranslateMaterialsButton.label': '매테리얼',
    'ManualPanel.delete': '제거:',
    'ManualPanel.RemoveZeroWeightBones.label': '제로 웨이트 본',
    'ManualPanel.RemoveConstraints': '컨스트레이트',
    'ManualPanel.RemoveZeroWeightGroups': '제로 웨이트 버텍스 그룹',
    'ManualPanel.normals': '노말:',
    'ManualPanel.RecalculateNormals.label': '재계산',
    'ManualPanel.FlipNormals.label': '뒤집기',
    'ManualPanel.fbtFix': '풀바디 트레킹 수정:',
    'ManualPanel.FixFBTButton.label': '추가',
    'ManualPanel.RemoveFBTButton.label': '제거',

    # UI Custom
    'CustomPanel.label': '커스텀 모델 제작',
    'CustomPanel.mergeArmatures': '뼈대(Armature) 통합:',
    'CustomPanel.warn.twoArmatures': '두개의 뼈대(Armature)가 필요합니다!',
    'CustomPanel.mergeInto': '베이스로',
    'CustomPanel.toMerge': '통합할 부분',
    'CustomPanel.attachToBone': '붙이기',
    'CustomPanel.armaturesCanMerge': '뼈대(Armature)들은 자동으로 통합됩니다!',
    'CustomPanel.attachMesh1': '메쉬를 뼈대(Armature)에 붙이기:',
    'CustomPanel.attachMesh2': '메쉬',
    'CustomPanel.warn.noArmOrMesh1': '뼈대(Armature)와 메쉬가 필요합니다!',
    'CustomPanel.warn.noArmOrMesh2': '메쉬에 부모가 없어야 합니다.',

    # UI Decimation
    'DecimationPanel.label': '축소(Decimation)',
    'DecimationPanel.decimationMode': '축소 모드:',
    'DecimationPanel.safeModeDesc': ' 괜찮은 결과 - 쉐이프키 손실 없음',
    'DecimationPanel.halfModeDesc': ' 나쁘지 않은 결과, - 최소한의 쉐이프키 손실됨',
    'DecimationPanel.fullModeDesc': ' 일관된 결과 - 모든 쉐이프키들이 손실됨',
    'DecimationPanel.smartModeDesc': ' 최고의 결과 - 쉐이프키들이 보존됨',
    'DecimationPanel.customSeparateMaterials': '매테리얼별로 분리하는 것으로 시작:',
    'DecimationPanel.SeparateByMaterials.label': '매테리얼별로 분리',
    'DecimationPanel.customJoinMeshes': '메쉬를 통합하여 중지:',
    'DecimationPanel.customWhitelist': '화이트리스트:',
    'DecimationPanel.warn.noShapekeySelected': '선택된 쉐이프키 없음',
    'DecimationPanel.warn.noDecimation': '모든 메쉬가 선택됨. 이것은 축소되지 않습니다.',
    'DecimationPanel.warn.noMeshSelected': '선택된 메쉬가 없음',
    'DecimationPanel.warn.emptyList': '양쪽 리스트들이 비어있어 전체 축소와 같습니다!',
    'DecimationPanel.warn.correctWhitelist': '양쪽 화이트리스트들은 축소 중에 고려됩니다.',
    'DecimationPanel.preset.excellent.label': 'Excellent',
    'DecimationPanel.preset.excellent.description': '당신의 아바타가 Excellent 등급을 받을 수 있는 최대 삼각폴리곤(Tris) 개수입니다.',
    'DecimationPanel.preset.good.label': 'Good',
    'DecimationPanel.preset.good.description': '당신의 아바타가 Good 등급을 받을 수 있는 최대 삼각폴리곤(Tris) 개수입니다.',
    'DecimationPanel.preset.quest.label': 'Quest',
    'DecimationPanel.preset.quest.description': '퀘스트용 아바타들을 위해 권장되는 삼각폴리곤(Tris)의 개수입니다.\n'
                                                '앞으로는 이보다 심하지는 않을 엄격한 제한이 설정될 것입니다.',
    'DecimationPanel.warn.notIfBaking': "베이킹 할 시 추천되지 않습니다!",

    # UI Eye tracking
    'EyeTrackingPanel.label': '눈 추적(Eye Tracking)',
    'EyeTrackingPanel.error.noMesh': '메쉬가 발견되지 않음!',
    'EyeTrackingPanel.error.noArm': '모델이 발견되지 않음!',
    'EyeTrackingPanel.error.wrongNameArm1': '뼈대는 반드시 \'Armature\'로 이름을 지어야 합니다.',
    'EyeTrackingPanel.error.wrongNameArm2': '      눈 추적(Eye Tracking)이 작동하기 위해!',
    'EyeTrackingPanel.error.wrongNameArm3': '      (현재로서는 \'',
    'EyeTrackingPanel.error.wrongNameBody1': '눈들을 포함한 메쉬는 반드시',
    'EyeTrackingPanel.error.wrongNameBody2': '      눈 추적(Eye Tracking)을 위해 \'Body\'로 이름을 지어야 합니다.',
    'EyeTrackingPanel.error.wrongNameBody3': '      (현재로서는 \'',
    'EyeTrackingPanel.warn.assignEyes1': '유니티에서 \'LeftEye\'와 \'RightEye\'를 ',
    'EyeTrackingPanel.warn.assignEyes2': '      적용하는 것을 잊지 마세요!',

    # UI Visemes
    'VisemePanel.label': '립싱크(Visemes)',
    'VisemePanel.error.noMesh': '메쉬가 발견되지 않음!',

    # UI Bone_root
    'BoneRootPanel.label': '본 부모설정',

    # UI Optimization
    'OptimizePanel.label': '최적화',
    'OptimizePanel.atlasDesc': '텍스처들을 결합시켜주는 더욱 향상된 아틀라스 생성기입니다.',
    'OptimizePanel.atlasAuthor': 'Made by Shotariya',
    'OptimizePanel.matCombDisabled1': '매테리얼 통합기가 활성화되지 않았습니다!',
    'OptimizePanel.matCombDisabled2': 'User preferences에서 이것을 활성화하세요:',
    'OptimizePanel.matCombOutdated1': '당신의 매테리얼 통합기의 버전이 낮습니다!',
    'OptimizePanel.matCombOutdated2': '최신버전으로 업데이트하세요.',
    'OptimizePanel.matCombOutdated3': '\'Updates\' 패널에서 업데이트하세요.',
    'OptimizePanel.matCombOutdated4': '\'MatCombiner\' 탭의 {location}',
    'OptimizePanel.matCombOutdated5_2.79': '왼쪽에 있습니다.',
    'OptimizePanel.matCombOutdated5_2.8': '오른쪽에 있습니다.',
    'OptimizePanel.matCombOutdated6': '혹은 직접 다운로드와 설치하기:',
    'OptimizePanel.matCombOutdated6_alt': '직접 다운로드와 설치하기:',
    'OptimizePanel.matCombNotInstalled': '매테리얼 통합기가 설치되지 않았습니다!',

    # UI Copy protection
    'CopyProtectionPanel.label': '복사핵 방지',
    'CopyProtectionPanel.desc1': '유니티 캐쉬뜨기로부터 당신의 아바타를 보호하세요.',
    'CopyProtectionPanel.desc2': '이 방법도 100% 안전하지는 않습니다!',
    'CopyProtectionPanel.desc3': '사용 전에: 문서를 읽어주세요!',

    # UI Bake
    'BakePanel.label': '베이크(Bake)',
    'BakePanel.versionTooOld': 'Blender 2.80 버전 이상에서만 호환',
    'BakePanel.autodetectlabel': '자동감지:',
    'BakePanel.generaloptionslabel': "일반 옵션:",
    'BakePanel.noheadfound': "\"Head\" 본 발견되지 않음!",
    'BakePanel.overlapfixlabel': "중복 수정:",
    'BakePanel.bakepasseslabel': "베이크 패스:",
    'BakePanel.alphalabel': "Alpha:",
    'BakePanel.transparencywarning': "현재 투명도가 선택되지 않았습니다!",
    'BakePanel.smoothnesswarning': "현재 부드러움이 선택되지 않았습니다!",
    'BakePanel.doublepackwarning': "두군데에 부드러움이 설정되었습니다!",

    # UI Settings & Updates
    'UpdaterPanel.label': '세팅 & 업데이트',
    'UpdaterPanel.name': '세팅:',
    'UpdaterPanel.requireRestart1': '재시작이 필요합니다.',
    'UpdaterPanel.requireRestart2': '일부 변경은 블렌더를 다시 시작해야합니다.',

    # UI Supporter
    'SupporterPanel.label': '후원자들',
    'SupporterPanel.desc': '이 플러그인을 마음에 드시고 우리를 후원하고 싶으신가요?',
    'SupporterPanel.thanks': '저희 멋진 후원자분들께 정말 감사합니다! <3',
    'SupporterPanel.missingName1': '당신의 이름이 빠졌나요?',
    'SupporterPanel.missingName2': '     부디 우리 디스코드 서버에서 연락해주시기 바랍니다!',

    # UI Credits
    'CreditsPanel.label': 'Credits',
    'CreditsPanel.desc1': 'Cats Blender Plugin (',
    'CreditsPanel.desc2': '멋진 VRChat 커뮤니티를 위해서',
    'CreditsPanel.desc3': 'Hotox와 GiveMeAllYourCats에 의해 제작됨 <3',
    'CreditsPanel.desc4': 'Special thanks to:',
    'CreditsPanel.descContributors': 'Feilen, Jordo, Ruubick, Shotariya와 Neitri',
    'CreditsPanel.desc5': '도움이 필요하시거나 혹시 버그를 찾으셨나요?',

    # Tools Armature
    'FixArmature.label': '모델 고치기',
    'FixArmature.desc': '자동으로 아래의 항목들이 고쳐집니다:\n'
                        '- 본들의 부모 재설정\n'
                        '- 필요하지 않는 본들, 오브젝트들, 그룹들과 컨스트레인트들을 제거\n'
                        '- 본들과 오브젝트들을 영어로 번역하고 이름들을 바꿈\n'
                        '- 웨이트 페인트들을 통합\n'
                        '- \'hips\'본을 고침\n'
                        '- 메쉬 통합\n'
                        '- morphs를 shapes로 변환\n'  # comment: I need more information about those.
                        '- 쉐이딩을 고침',
    'FixArmature.error.noMesh': ['뼈대(Armature) 안에 메쉬가 없습니다!',
                                 '만약 뼈대 밖에 메쉬들이 있다면,',
                                 '그 뼈대를 메쉬들의 부모로 설정하세요.'],
    # Format strings? vvvv t(str, fixed_uv_coords) -> The model was successfully fixed, but there were {} faulty UV
    'FixArmature.error.faultyUV1': '모델이 성공적으로 고쳐졌지만, 잘못된 UV 좌표들이 있습니다. {uvcoord}',
    # 'The model was successfully fixed, but there were ' + str(fixed_uv_coords) + ' faulty UV coordinates.',
    'FixArmature.error.faultyUV2': '이것은 텍스처를 망가뜨리는 결과를 불러올 수 있으며 당신이 그것들을 직접 손봐야할 수 있습니다.',
    'FixArmature.error.faultyUV3': '이 이슈는 자주 PMX editor에서 편집할 경우 일어날 수 있습니다.',
    'FixArmature.fixedSuccess': '모델이 성공적으로 고쳐졌습니다.',
    'FixArmature.bonesNotFound': '해당 본들이 발견되지 않았습니다:',
    'FixArmature.cantFix1': 'Cats Plugin이 고칠 수 없는 모델인 것 같습니다!',
    'FixArmature.cantFix2': '이것이 수정되지 않은 모델이라면 우리는 호환되도록 만들고 싶습니다.',
    'FixArmature.cantFix3': '포럼이나 디스코드에서 우리에게 신고해주세요. 링크는 크레딧 패널에 있습니다.',
    'FixArmature.notParent': ' 부모설정이 전혀 안됐다면, 이로 인해 문제가 발생할 수 있습니다!',
    'FixArmature.notParentTo1': ' 가 ',
    'FixArmature.notParentTo2': '의 부모로 설정돼지 않았다면, 이로 인해 문제가 발생할 수 있습니다!',

    # Tools Armature Manual
    'StartPoseMode.label': '포즈모드 시작',
    'StartPoseMode.desc': '포즈모드를 시작합니다.\n'
                          '이것은 당신의 모델이 어떻게 움직일지 테스트할 수 있게 해줍니다',
    'StartPoseModeNoReset.desc': '포즈 재설정없이 포즈모드를 시작합니다.\n'
                                 '이것은 당신의 모델이 어떻게 움직일지 테스트할 수 있게 해줍니다',

    'StopPoseMode.label': '포즈모드 중단',
    'StopPoseMode.desc': '포즈모드를 중단하고 포즈를 초기상태로 되돌립니다',
    'StopPoseModeNoReset.desc': '포즈모드를 중단하고 현재 포즈를 유지합니다',

    'PoseToShape.label': '현재 포즈를 쉐이프키로 만들기',
    'PoseToShape.desc': '이것은 당신의 현재 포즈를 새로운 쉐이프키로 만듭니다.'
                        '\n새로운 쉐이프키는 메쉬의 쉐이프키 리스트의 제일 아래에 생성됩니다.',

    'PoseNamePopup.label': '쉐이프키의 이름 설정:',
    'PoseNamePopup.desc': '쉐이프키 이름을 설정합니다. 스킵하려면 아무 곳이나 누르세요.',
    'PoseNamePopup.success': '포즈가 성공적으로 쉐이프키로 저장되었습니다.',

    'PoseToRest.label': '새로운 기본자세로 적용',
    'PoseToRest.desc': '이것은 현재 포즈를 새로운 기본 포즈로 적용합니다.'
                       '\n'
                       '\n만약 당신이 뼈들의 스케일을 각 축마다 동일하게 조절했다면 쉐이프키들 또한 올바르게 적용될 것입니다!'
                       '\n경고: 이것은 쉐이프키에 원치 않는 영향을 줄 수 있기 때문에, 이걸로 머리를 수정할 경우 조심하세요.',
    'PoseToRest.success': '포즈가 성공적으로 기본자세로 적용되었습니다.',

    'JoinMeshes.label': '메쉬 통합',
    'JoinMeshes.desc': '모델의 모든 메쉬들을 통합시킵니다.'
                       '\n또한:'
                       '\n  - 모든 쉐이프키들의 순서를 올바르게 재설정합니다.'
                       '\n  - 모든 변환(Transforms)을 적용'
                       '\n  - 망가진 아마추어 모디파이어들(armature modifiers)을 고침'
                       '\n  - 모든 데시메이션(decimation)과 미러 모디파이어들(mirror modifiers)을 적용'
                       '\n  - UV맵들을 올바르게 통합',
    'JoinMeshes.failure': '메쉬들이 통합될 수 없었습니다!',
    'JoinMeshes.success': '메쉬들이 통합됐습니다.',

    'JoinMeshesSelected.label': 'Join Selected Meshes',
    'JoinMeshesSelected.desc': '모델의 모든 메쉬들을 통합시킵니다.'
                            '\n또한:'
                            '\n  - 모든 쉐이프키들의 순서를 올바르게 재설정합니다.'
                            '\n  - 모든 변환(Transforms)을 적용'
                            '\n  - 망가진 아마추어 모디파이어들(armature modifiers)을 고침'
                            '\n  - 모든 데시메이션(decimation)과 미러 모디파이어들(mirror modifiers)을 적용'
                            '\n  - UV맵들을 올바르게 통합',
    'JoinMeshesSelected.error.noSelect': '선택된 메쉬들이 없습니다! 합치고 싶은 메쉬들을 계층(Hierarchy) 창에서 선택해주세요!',
    'JoinMeshesSelected.error.cantJoin': '선택된 메쉬들이 통합될 수 없었습니다!',
    'JoinMeshesSelected.success': '선택된 메쉬들이 통합됐습니다.',

    'SeparateByMaterials.label': '매테리얼별로 분리하기',
    'SeparateByMaterials.desc': '선택된 메쉬를 매테리얼 별로 나눕니다.\n'
                                '\n'
                                '경고: 나중에 쉐이프키가 필요한 것들은 절대 데시메이트하지 마십시오. (얼굴, 입, 눈 등..)',
    'SeparateByMaterials.success': '성공적으로 매테리얼별로 분리됐습니다.',

    'SeparateByLooseParts.label': '느슨한 부분들로 분리하기',
    'SeparateByLooseParts.desc': '선택된 메쉬를 느슨한 부분들별로 나눕니다.\n'
                                 '이것은 매테리얼별로 분리시키는 것과 같지만 보다 높은 정확도를 위해 더 많은 메쉬들을 만듭니다',
    'SeparateByLooseParts.success': '성공적으로 느슨한 부분들로 분리됐습니다.',

    'SeparateByShapekeys.label': '쉐이프키별로 분리하기',
    'SeparateByShapekeys.desc': '선택된 메쉬를 두 부분으로 나누는데,'
                                '\n쉐이프키에 의해 영향을 받는지 여부에 따라 결정됩니다.'
                                '\n'
                                '\n수동으로 데시메이션을 할 시 매우 유용합니다',
    'SeparateByShapekeys.success': '성공적으로 쉐이프키별로 분리됐습니다.',

    'SeparateByCopyProtection.label': '복사핵 방지별로 분리하기 Separate by Copy Protection',
    'SeparateByCopyProtection.desc': '선택된 메쉬를 두 부분으로 나누는데,'
                                     '\nCats의 복사핵 방지의 영향을 받는지 여부에 따라 결정됩니다.'
                                     '\n'
                                     '\n모델의 여러 부분에서 복사 방지를 활성화 한 경우 유용합니다.',
    'SeparateByCopyProtection.success': '성공적으로 쉐이프키별로 분리됐습니다.',

    'SeparateByX.error.noMesh': '메쉬가 발견되지 않음!',
    'SeparateByX.error.multipleMesh': '여러 메쉬들이 발견됨!'
                                      '\n나누고 싶은 메쉬를 선택해주세요!',
    'SeparateByX.warn.noSeparation': '메쉬를 분리 할 필요가 없습니다!',

    'MergeWeights.label': '부모쪽으로 웨이트들을 통합',
    'MergeWeights.desc': 'Deletes the selected bones and adds their weight to their respective parents.'
                         '\n'
                         '\nOnly available in Edit or Pose Mode with bones selected',
    'MergeWeights.success': 'Deleted {number} bones and added their weights to their parents.',

    'MergeWeightsToActive.label': '웨이트를 활성화된 본으로 통합',
    'MergeWeightsToActive.desc': 'Deletes the selected bones except the active one and adds their weights to the active bone.'
                                 '\nThe active bone is the one you selected last.'
                                 '\n'
                                 '\nOnly available in Edit or Pose Mode with bones selected',
    'MergeWeightsToActive.success': 'Deleted {number} bones and added their weights to the active bone.',

    'ApplyTransformations.label': '변환 적용',
    'ApplyTransformations.desc': 'Applies the position, rotation and scale to the armature and it\'s meshes',
    'ApplyTransformations.success': 'Transformations applied.',

    'ApplyAllTransformations.label': '모든 변환 적용',
    'ApplyAllTransformations.desc': 'Applies the position, rotation and scale of all objects',
    'ApplyAllTransformations.success': 'Transformations applied.',

    'RemoveZeroWeightBones.label': '제로웨이트 본들 제거',
    'RemoveZeroWeightBones.desc': 'Cleans up the bones hierarchy, deleting all bones that don\'t directly affect any vertices\n'
                                  'Don\'t use this if you plan to use \'Fix Model\'',
    'RemoveZeroWeightBones.success': 'Deleted {number} zero weight bones.',

    'RemoveZeroWeightGroups.label': '제로웨이트 버텍스 그룹들 제거',
    'RemoveZeroWeightGroups.desc': 'Cleans up the vertex groups of all meshes, deleting all groups that don\'t directly affect any vertices',
    'RemoveZeroWeightGroups.success': 'Removed {number} zero weight vertex groups.',

    'RemoveConstraints.label': '본 컨스트레인트들 제거',
    'RemoveConstraints.desc': 'Removes constrains between bones causing specific bone movement as these are not used by VRChat',
    'RemoveConstraints.success': 'Removed all bone constraints.',

    'RecalculateNormals.label': '노말 재계산',
    'RecalculateNormals.desc': 'Makes normals point inside of the selected mesh.\n\n'
                               'Don\'t use this on good looking meshes as this can screw them up.\n'
                               'Use this if there are random inverted or darker faces on the mesh',
    'RecalculateNormals.success': 'Recalculated all normals.',

    'FlipNormals.label': '노말 뒤집기',
    'FlipNormals.desc': 'Flips the direction of the faces\' normals of the selected mesh.\n'
                        'Use this if all normals are inverted',
    'FlipNormals.success': 'Flipped all normals.',

    'RemoveDoubles.label': '이중 제거',
    'RemoveDoubles.desc': '선택한 메시의 중복 면들(faces)과 점(vertices)을 병합합니다.'
                          '\nThis is more safe than doing it manually:'
                          '\n  - leaves shape keys completely untouched'
                          '\n  - but removes less doubles overall',
    'RemoveDoubles.success': 'Removed {number} vertices.',

    'RemoveDoublesNormal.label': '일반적으로 이중 제거',
    'RemoveDoublesNormal.desc': '선택한 메시의 중복 면들(faces)과 점(vertices)을 병합합니다.'
                                '\nThis is exactly like doing it manually',
    'RemoveDoublesNormal.success': 'Removed {number} vertices.',

    'FixVRMShapesButton.label': '코이카츠 쉐이프키 고치기',
    'FixVRMShapesButton.desc': 'Fixes the shapekeys of Koikatsu models',
    'FixVRMShapesButton.warn.notDetected': 'No shapekeys detected!',
    'FixVRMShapesButton.success': 'Fixed VRM shapekeys.',

    'FixFBTButton.label': '풀바디 트래킹 적용',
    'FixFBTButton.desc': 'WARNING: This fix is no longer needed for VRChat, you should not use it!'
                         '\n'
                         '\nApplies a general fix for Full Body Tracking.'
                         '\nIgnore the \"Spine length zero\" warning in Unity',
    'FixFBTButton.error.bonesNotFound': 'Required bones could not be found!'
                                        '\nPlease make sure that your armature contains the following bones:'
                                        '\n - Hips, Spine, Left leg, Right leg'
                                        '\nExact names are required!',
    'FixFBTButton.error.alreadyApplied': 'Full Body Tracking Fix already applied!',
    'FixFBTButton.success': 'Successfully applied the Full Body Tracking fix.',

    'RemoveFBTButton.label': '풀바디 트래킹 적용 제거',
    'RemoveFBTButton.desc': 'Removes the fix for Full Body Tracking, since it is no longer advised to use it.'
                            '\n'
                            '\nRequires bones:'
                            '\n - Hips, Spine, Left leg, Right leg, Left leg 2, Right leg 2',
    'RemoveFBTButton.error.bonesNotFound': 'Required bones could not be found!'
                                           '\nPlease make sure that your armature contains the following bones:'
                                           '\n - Hips, Spine, Left leg, Right leg, Left leg 2, Right leg 2'
                                           '\nExact names are required!',
    'RemoveFBTButton.error.notApplied': 'The Full Body Tracking Fix is not applied!',
    'RemoveFBTButton.success': 'Successfully removed the Full Body Tracking fix.',

    'DuplicateBonesButton.label': '본 복사',
    'DuplicateBonesButton.desc': 'Duplicates the selected bones including their weight and renames them to _L and _R',
    'DuplicateBonesButton.success': 'Successfully duplicated {number} bones.',

    # Tools Armature Custom
    'MergeArmature.label': '뼈대(Armatures) 통합',
    'MergeArmature.desc': 'Merges the selected merge armature into the base armature.'
                          '\nYou should fix both armatures with Cats first.'
                          '\nOnly move the mesh of the merge armature to the desired position, the bones will be moved automatically',
    'MergeArmature.error.notFound': 'The armature "{name}" could not be found.',
    'MergeArmature.error.checkTransforms': ['Please make sure that the parent of the merge armature has the following transforms:',
                                            ' - Location at 0',
                                            ' - Rotation at 0',
                                            ' - Scale at 1'],
    'MergeArmature.error.pleaseFix': ['Please use the "Fix Model" feature on the selected armatures first!',
                                      'Make sure to select the armature you want to fix above the "Fix Model" button!',
                                      'After that please only move the mesh (not the armature!) to the desired position.'],
    'MergeArmature.success': 'Armatures successfully joined.',

    'AttachMesh.label': '메쉬에 붙이기',
    'AttachMesh.desc': 'Attaches the selected mesh to the selected bone of the selected armature.'
                       '\n'
                       '\nINFO: The mesh will only be assigned to the selected bone.'
                       '\nE.g.: A jacket won\'t work, because it requires multiple bones',
    'AttachMesh.success': 'Mesh successfully attached to armature.',

    'CustomModelTutorialButton.label': '사용법',
    'CustomModelTutorialButton.URL': 'https://github.com/michaeldegroot/cats-blender-plugin#custom-model-creation',  # BOOM, now we can point at the Japanese link now ;)
    'CustomModelTutorialButton.success': 'Documentation opened.',

    'merge_armatures.error.transformReset': ['If you want to rotate the new part, only modify the mesh instead of the armature,',
                                             'or select "Apply Transforms"!',
                                             '',
                                             'The transforms of the merge armature got reset and the mesh you have to modify got selected.',
                                             'Now place this selected mesh where and how you want it to be and then merge the armatures again.',
                                             'If you don\'t want that, undo this operation.'],
    'merge_armatures.error.pleaseUndo': ['Something went wrong! Please undo, check your selections and try again.'],

    # Tools Atlas
    'EnableSMC.label': '매테리얼 통합기 활성화',
    'EnableSMC.desc': 'Enables Material Combiner',
    'EnableSMC.success': 'Enabled Material Combiner!',

    'AtlasHelpButton.label': '매테리얼 목록 생성',
    'AtlasHelpButton.desc': 'Open useful Atlas Tips',
    'AtlasHelpButton.URL': 'https://github.com/michaeldegroot/cats-blender-plugin/#texture-atlas',
    'AtlasHelpButton.success': 'Atlas Help opened.',

    'InstallShotariya.label': '매테리얼 통합기를 로드하는 중 오류 발생:',
    'InstallShotariya.error.install1': 'Material Combiner is not installed!',
    'InstallShotariya.error.install2': 'The plugin \'Material Combiner\' by Shotariya is required for this function.',
    'InstallShotariya.error.install3': 'Please download and install it manually:',
    'InstallShotariya.error.enable1': 'Material Combiner is not enabled!',
    'InstallShotariya.error.enable2': 'The plugin \'Material Combiner\' by Shotariya is required for this function.',
    'InstallShotariya.error.enable3': 'Please enable it in your User Preferences.',
    'InstallShotariya.error.version1': 'Material Combiner is outdated!',
    'InstallShotariya.error.version2': 'The latest version is required for this function.',
    'InstallShotariya.error.version3': 'Please download and install it manually:',

    'ShotariyaButton.label': '매테리얼 통합기 다운로드',
    'ShotariyaButton.URL': 'https://vrcat.club/threads/material-combiner-blender-addon-1-1-3.2255/',
    'ShotariyaButton.success': 'Material Combiner link opened',

    # Tools Bonemerge
    'BoneMergeButton.label': '뼈 통합',
    'BoneMergeButton.desc': 'Merges the given percentage of bones together.\n'
                            'This is useful to reduce the amount of bones used by Dynamic Bones.',
    'BoneMergeButton.success': 'Merged bones.',

    # Tools Common
    'ShowError.label': 'Report: Error',

    # Tools Copy protection
    'CopyProtectionEnable.label': '보호 활성화',
    'CopyProtectionEnable.desc': 'Protects your model from piracy. NOT a 100% safe protection!'
                                 '\nRead the documentation before use',
    'CopyProtectionEnable.success': 'Model secured!',

    'CopyProtectionDisable.label': '보호 비활성화',
    'CopyProtectionDisable.desc': 'Removes the copy protections from this model.',
    'CopyProtectionDisable.success': 'Model un-secured!',

    'ProtectionTutorialButton.label': '문서로 이동',
    'ProtectionTutorialButton.URL': 'https://github.com/michaeldegroot/cats-blender-plugin#copy-protection',
    'ProtectionTutorialButton.success': 'Documentation',

    # Tools Credits
    'ForumButton.label': '포럼으로 가기',
    'ForumButton.URL': 'https://vrcat.club/threads/cats-blender-plugin.6/',
    'ForumButton.success': 'Forum opened.',

    'DiscordButton.label': '우리 디스코드에 가입하기',
    'DiscordButton.URL': 'https://discord.gg/f8yZGnv',
    'DiscordButton.success': 'Discord opened.',

    'PatchnotesButton.label': '최신 패치노트',
    'PatchnotesButton.URL': 'https://github.com/michaeldegroot/cats-blender-plugin/releases',
    'PatchnotesButton.success': 'Patchnotes opened.',

    # Tools Decimation
    'ScanButton.label': '축소모델 검색',
    'ScanButton.desc': 'Separates the mesh.',

    'AddShapeButton.label': 'Add',
    'AddShapeButton.desc': 'Adds the selected shape key to the whitelist.\n'
                           'This means that every mesh containing that shape key will be not decimated.',

    'AddMeshButton.label': 'Add',
    'AddMeshButton.desc': 'Adds the selected mesh to the whitelist.\n'
                          'This means that this mesh will be not decimated.',

    'RemoveShapeButton.label': '',
    'RemoveShapeButton.desc': 'Removes the selected shape key from the whitelist.\n'
                              'This means that this shape key is no longer decimation safe!',

    'RemoveMeshButton.label': '',
    'RemoveMeshButton.desc': 'Removes the selected mesh from the whitelist.\n'
                             'This means that this mesh will be decimated.',

    'AutoDecimateButton.label': '빠른 축소(Decimation)',
    'AutoDecimateButton.desc': 'This will automatically decimate your model while preserving the shape keys.\n'
                               'You should manually remove unimportant meshes first.',
    'AutoDecimateButton.error.noMesh': '메쉬가 발견되지 않음!',

    'decimate.cantDecimateWithSettings': 'This model can not be decimated to {number} tris with the specified settings.',
    'decimate.safeTryOptions': 'Try to use Custom, Half or Full Decimation.',
    'decimate.halfTryOptions': 'Try to use Custom or Full Decimation.',
    'decimate.customTryOptions': 'Select fewer shape keys and/or meshes or use Full Decimation.',
    'decimate.disableFingersOrIncrease': 'Disable \'Save Fingers\' or increase the Tris Count.',
    'decimate.disableFingers': 'or disable \'Save Fingers\'.',  # This comes after one of the previous xTryOptions
    'decimate.noDecimationNeeded': 'The model already has less than {number} tris. Nothing had to be decimated.',
    'decimate.cantDecimate1': 'The model could not be decimated to {number} tris.',
    'decimate.cantDecimate2': 'It got decimated as much as possible within the limits.',

    # Tools Eyetracking
    'CreateEyesButton.label': '눈 추적(Eye Tracking) 생성',
    'CreateEyesButton.desc': '누군가가 가까이 왔을 때 그 사람을 추적 할 수 있고 눈 깜박임을 가능하게합니다.\n'
                             '데시메이션이 필요하다면 이 작업 이전에 해야합니다.\n'
                             '눈 움직임을 \'Testing\' 탭에서 테스트하세요.',
    'CreateEyesButton.error.noShapeSelected': '선택된 쉐이프키가 없습니다.'
                                              '\n쉐이프키가 포함 된 메쉬를 선택하거나 "눈 깜빡임 비활성화"에 체크하세요.',
    'CreateEyesButton.error.missingBone': 'The bone "{bone}" does not exist.',
    'CreateEyesButton.error.noVertex': 'The bone "{bone}" has no existing vertex group or no vertices assigned to it.'
                                       '\nThis might be because you selected the wrong mesh or the wrong bone.'
                                       '\nAlso make sure that the selected eye bones actually move the eyes in pose mode.',
    'CreateEyesButton.error.dontUse': 'Please do not use "{eyeName}" as the input bone.'
                                      '\nIf you are sure that you want to use that bone please rename it to "{eyeNameShort}".',
    'CreateEyesButton.error.hierarchy': 'Eye tracking will not work unless the bone hierarchy is exactly as following: Hips > Spine > Chest > Neck > Head'
                                        '\nFurthermore the mesh containing the eyes has to be called "Body" and the armature "Armature".',
    'CreateEyesButton.success': 'Created eye tracking!',

    'StartTestingButton.label': '아이테스트 시작',
    'StartTestingButton.desc': 'This will let you test how the eye movement will look ingame.\n'
                               'Don\'t forget to stop the Testing process afterwards.\n'
                               'Bones "LeftEye" and "RightEye" are required.',

    'StopTestingButton.label': '아이테스트 중지',
    'StopTestingButton.desc': 'Stops the testing process.',
    'StopTestingButton.error.tryAgain': 'Something went wrong. Please try eye testing again.',

    'ResetRotationButton.label': '회전 초기화',
    'ResetRotationButton.desc': 'This resets the eye positions.',

    'AdjustEyesButton.label': '범위 설정',
    'AdjustEyesButton.desc': 'Lets you re-adjust the movement range of the eyes.\n'
                             'This gets saved',
    'AdjustEyesButton.error.noVertex': 'The bone "{bone}" has no existing vertex group or no vertices assigned to it.'
                                       '\nThis might be because you selected the wrong mesh or the wrong bone.'
                                       '\nAlso make sure to join your meshes before creating eye tracking and make sure that the eye bones actually move the eyes in pose mode.',

    'StartIrisHeightButton.label': '눈동자 높이 조정 시작',
    'StartIrisHeightButton.desc': 'Lets you readjust the distance of the iris from the eye ball.\n'
                                  'Use this to fix clipping of the iris into the eye ball.\n'
                                  'This gets saved.',

    'TestBlinking.label': '테스트',
    'TestBlinking.desc': '게임 중에 눈 깜박임이 어떻게 보이는 지 확인할 수 있습니다.',

    'TestLowerlid.label': '테스트',
    'TestLowerlid.desc': '게임 중에 아래 눈꺼풀이 어떻게 보이는 지 확인할 수 있습니다.',

    'ResetBlinkTest.label': '쉐이프 초기화',
    'ResetBlinkTest.desc': '눈깜빡임 테스트를 초기화한다.',

    # Tools Importer
    'ImportAnyModel.label': '아무 모델 불러오기',
    'ImportAnyModel.desc2.79': 'Import a model of any supported type.'
                               '\n'
                               '\nSupported types:'
                               '\n- MMD: .pmx/.pmd'
                               '\n- XNALara: .xps/.mesh/.ascii'
                               '\n- Source: .smd/.qc'
                               '\n- VRM: .vrm'
                               '\n- FBX .fbx '
                               '\n- DAE: .dae '
                               '\n- ZIP: .zip',
    'ImportAnyModel.desc2.8': 'Import a model of any supported type.'
                              '\n'
                              '\nSupported types:'
                              '\n- MMD: .pmx/.pmd'
                              '\n- XNALara: .xps/.mesh/.ascii'
                              '\n- Source: .smd/.qc/.vta/.dmx'
                              '\n- VRM: .vrm'
                              '\n- FBX: .fbx'
                              '\n- DAE: .dae '
                              '\n- ZIP: .zip',
    'ImportAnyModel.importantInfo.label': 'IMPORTANT INFO (hover here)',
    'ImportAnyModel.importantInfo.desc': 'If you want to modify the import settings, use the button next to the Import button.\n\n',
    'ImportAnyModel.error.emptyZip': 'The selected zip file contains no importable models.',
    'ImportAnyModel.error.unsupportedFBX': 'The FBX file version is unsupported!'
                                           '\nPlease use a tool such as the "Autodesk FBX Converter" to make it compatible.',

    'ZipPopup.label': 'Zip 모델 선택:',
    'ZipPopup.desc': 'zip 파일에 포함된 모델들을 보여준다',
    'ZipPopup.selectModel1': 'Select which model you want to import',
    'ZipPopup.selectModel2': 'Then confirm with OK',

    'get_zip_content.choose': 'Import model "{model}" from the zip "{zipName}?"',

    'ModelsPopup.label': '불러올 것을 선택:',
    'ModelsPopup.desc': 'Show individual import options',

    'ImportMMD.label': 'MMD',
    'ImportMMD.desc': 'Import a MMD model (.pmx/pmd)',

    'ImportXPS.label': 'XNALara',
    'ImportXPS.desc': 'Import a XNALara model (.xps/.mesh/.ascii)',

    'ImportSource.label': 'Source',
    'ImportSource.desc': 'Import a Source model (.smd/.qc/.vta/.dmx)',

    'ImportFBX.label': 'FBX',
    'ImportFBX.desc': 'Import a FBX model (.fbx)',

    'ImportVRM.label': 'VRM',
    'ImportVRM.desc': 'Import a VRM model (.vrm)',

    'InstallXPS.label': 'XPS Tools is not installed or enabled!',

    'InstallSource.label': 'Source Tools is not installed or enabled!',

    'InstallVRM.label': 'VRM Importer is not installed or enabled!',

    'InstallX.pleaseInstall1': 'If it is not enabled please enable it in your User Preferences.',
    'InstallX.pleaseInstall2': 'If it is not installed please download and install it manually.',
    'InstallX.pleaseInstall3': 'Make sure to install the version for Blender {blenderVersion}',
    'InstallX.pleaseInstallTesting': 'Currently you have to select \'Testing\' in the addons settings.',

    'EnableMMD.label': 'Mmd_tools가 활성화되지 않음!',
    'EnableMMD.required1': 'The plugin "mmd_tools" is required for this function.',
    'EnableMMD.required2': 'Please restart Blender.',

    'XpsToolsButton.label': 'XPS Tools 다운로드',
    'XpsToolsButton.URL': 'https://github.com/johnzero7/XNALaraMesh',
    'XpsToolsButton.success': 'XPS Tools link opened',

    'SourceToolsButton.label': 'Source Tools 다운로드',
    'SourceToolsButton.URL': 'https://github.com/Artfunkel/BlenderSourceTools',
    'SourceToolsButton.success': 'Source Tools link opened',

    'VrmToolsButton.label': 'VRM Importer 다운로드',
    'VrmToolsButton.URL_2.79': 'https://github.com/iCyP/VRM_IMPORTER_for_Blender2_79',
    'VrmToolsButton.URL_2.8': 'https://github.com/saturday06/VRM_IMPORTER_for_Blender2_8',
    'VrmToolsButton.success': 'VRM Importer link opened',

    'ExportModel.label': '모델 내보내기',
    'ExportModel.desc': 'Export this model as .fbx for Unity.\n'
                        '\n'
                        'Automatically sets the optimal export settings',
    'ExportModel.error.notEnabled': 'FBX Exporter not enabled! Please enable it in your User Preferences.',

    'ErrorDisplay.label': '경고:',
    'ErrorDisplay.polygons1': 'Too many polygons!',
    'ErrorDisplay.polygons2': 'You have {number} tris in this model, but you shouldn\'t have more than 70,000!',
    'ErrorDisplay.polygons3': 'You should decimate before you export this model.',
    'ErrorDisplay.materials1': 'Model not optimized!',
    'ErrorDisplay.materials2': 'This model has {number} materials!',
    'ErrorDisplay.materials3': 'You should try to have a maximum of 4 materials on your model.',
    'ErrorDisplay.materials4': 'Creating a texture atlas in CATS is very easy, so please make use of it.',
    'ErrorDisplay.meshes1': 'Meshes not joined!',
    'ErrorDisplay.meshes2': 'This model has {number} meshes!',
    'ErrorDisplay.meshes3': 'It is not very optimized and might cause lag for you and others!',
    'ErrorDisplay.meshes3_alt': "It is extremely unoptimized and will cause laugh for you and others!",
    'ErrorDisplay.meshes4': 'You should always join your meshes, it\'s very easy:',
    'ErrorDisplay.JoinMeshes.label': '메쉬 통합',
    'ErrorDisplay.brokenShapekeys1': 'Broken shapekeys!',
    'ErrorDisplay.brokenShapekeys2': 'This model has {number} broken shapekey(s):',
    'ErrorDisplay.brokenShapekeys3': 'You will not be able to upload this model until you fix these shapekeys.',
    'ErrorDisplay.brokenShapekeys4': 'Either delete or repair them before export.',
    'ErrorDisplay.textures1': 'No textures found!',
    'ErrorDisplay.textures2': 'This model has no textures assigned but you have \'Embed Textures\' enabled.',
    'ErrorDisplay.textures3': 'Therefore, no textures will be embedded into the FBX.',
    'ErrorDisplay.textures4': 'This is not an issue, but you will have to import the textures manually into Unity.',
    'ErrorDisplay.eyes1': 'Eyes not named \'Body\'!',
    'ErrorDisplay.eyes2': 'The mesh \'{name}\' has Eye Tracking shapekeys but is not named \'Body\'.',
    'ErrorDisplay.eyes2_alt': 'Multiple meshes have Eye Tracking shapekeys but are not named \'Body\'.',
    'ErrorDisplay.eyes3': 'If you want Eye Tracking to work, rename this mesh to \'Body\'.',
    'ErrorDisplay.eyes3_alt': 'Make sure that the mesh containing the eyes is named \'Body\' in order',
    'ErrorDisplay.eyes4_alt': 'to get Eye Tracking to work.',
    'ErrorDisplay.continue': 'Continue to Export',

    # Tools Material
    'OneTexPerMatButton.label': '매테리얼당 하나의 텍스처',
    'OneTexPerMatButton.desc': 'Have all material slots ignore extra texture slots as these are not used by VRChat.',

    'OneTexPerMatOnlyButton.label': '매테리얼당 하나의 텍스처',
    'OneTexPerMatOnlyButton.desc': 'Have all material slots ignore extra texture slots as these are not used by VRChat.'
                                   '\nAlso removes the textures from the material instead of disabling it.'
                                   '\nThis makes no difference, but cleans the list for the perfectionists',

    'ToolsMaterial.error.notCompatible': 'This function is not yet compatible with Blender 2.8!',
    'OneTexPerXButton.success': 'All materials have one texture now.',

    'StandardizeTextures.label': '텍스처들 표준화',
    'StandardizeTextures.desc': 'Enables Color and Alpha on every texture, sets the blend method to Multiply'
                                '\nand changes the materials transparency to Z-Transparency',
    'StandardizeTextures.success': 'All textures are now standardized.',

    'CombineMaterialsButton.label': '같은 매테리얼들을 통합',
    'CombineMaterialsButton.desc': 'Combines similar materials into one, reducing draw calls.\n'
                                   'Your avatar should visibly look the same after this operation.\n'
                                   'This is a very important step for optimizing your avatar.\n'
                                   'If you have problems with this, please tell us!\n',
    'CombineMaterialsButton.error.noChanges': 'No materials combined.',
    'CombineMaterialsButton.success': 'Combined {number} materials!',

    'ConvertAllToPngButton.label': '텍스처를 PNG로 변환',
    'ConvertAllToPngButton.desc': 'Converts all texture files into PNG files.'
                                  '\nThis helps with transparency and compatibility issues.'
                                  '\n\nThe converted image files will be saved next to the old ones',
    'ConvertAllToPngButton.success': 'Converted {number} to PNG files.',

    # Tools Root bone
    'RootButton.label': '부모 본',
    'RootButton.desc': 'This will duplicate the parent of the bones and reparent them to the duplicate.\n'
                       'Very useful for Dynamic Bones.',
    'RootButton.success': 'Bones parented!',

    'RefreshRootButton.label': '목록 새로고침',
    'RefreshRootButton.desc': 'This will clear the group bones list cache and rebuild it, useful if bones have changed or your model.',
    'RefreshRootButton.success': 'Root bones refreshed, check the root bones list again.',

    # Tools Settings
    'RevertChangesButton.label': '설정 되돌리기',
    'RevertChangesButton.desc': '변경 사항을 Blender 시작했을 때의 설정으로 되돌립니다.',
    'RevertChangesButton.success': '설정 복구됨.',

    'ResetGoogleDictButton.label': '로컬 Google 번역 지우기',
    'ResetGoogleDictButton.desc': '현재 저장된 모든 Google 번역을 삭제합니다. 이 작업은 취소 할 수 없습니다.',
    'ResetGoogleDictButton.resetInfo': '로컬 Google 사전이 삭제되었습니다!',

    'DebugTranslations.label': 'Google 번역 디버그',  # DEV ONLY
    'DebugTranslations.desc': 'Tests Google translations and prints the response into a file called \'google-response.txt\' located in the cats addon folder > resources'
                              '\nThis button is only visible in the cats development version',  # DEV ONLY
    'DebugTranslations.error': 'Errors found, response printed!!',  # DEV ONLY
    'DebugTranslations.success': 'No issues with Google Translations found, response printed!',  # DEV ONLY

    # Tools Shapekey
    'ShapeKeyApplier.label': '선택된 쉐이프키를 Basis에 적용',
    'ShapeKeyApplier.desc': 'Applies the selected shape key to the new Basis at it\'s current strength and creates a reverted shape key from the selected one',
    'ShapeKeyApplier.error.revertCustomBasis': ['To revert the shape keys, please apply the "Reverted" shape keys in reverse order.',
                                                'Start with the shape key called "{name}".',
                                                '',
                                                'If you didn\'t change the shape key order, you can revert the shape keys from top to bottom.'],
    'ShapeKeyApplier.error.revertCustomBasis.scale': 7.3,
    'ShapeKeyApplier.error.revert': ['To revert the shape keys, please apply the "Reverted" shape keys in reverse order.',
                                     'Start with the reverted shape key that uses the relative key called "Basis".',
                                     '',
                                     "If you didn't change the shape key order, you can revert the shape keys from top to bottom."],
    'ShapeKeyApplier.error.revert.scale': 7.3,
    'ShapeKeyApplier.successRemoved': 'Successfully removed shapekey "{name}" from the Basis.',
    'ShapeKeyApplier.successSet': 'Successfully set shapekey "{name}" as the new Basis.',

    'addToShapekeyMenu.ShapeKeyApplier.label': '선택된 쉐이프키를 Basis에 적용',

    # Tools Supporter
    'PatreonButton.label': '후원자 되기',
    'PatreonButton.URL': 'https://www.patreon.com/catsblenderplugin',
    'PatreonButton.success': 'Patreon page opened.',

    'ReloadButton.label': '목록 새로고침',
    'ReloadButton.desc': '후원자 목록을 다시 불러옵니다',

    'DynamicPatronButton.label': '후원자 이름',
    'DynamicPatronButton.desc': '이것은 멋진 후원자입니다!',

    'register_dynamic_buttons.desc': '{name}는 멋진 후원자입니다!',

    # Tools Translate
    'TranslateShapekeyButton.label': '쉐이프키 이름 번역',
    'TranslateShapekeyButton.desc': '모든 쉐이프키들을 내장된 사전과 구글번역을 이용해 영어로 번역합니다.',
    'TranslateShapekeyButton.success': '{number}개의 쉐이프키들이 번역되었습니다.',

    'TranslateBonesButton.label': '본 이름 번역',
    'TranslateBonesButton.desc': '모든 본들을 내장된 사전과 구글번역을 이용해 영어로 번역합니다.',
    'TranslateBonesButton.success': '{number}개의 본들이 번역되었습니다.',

    'TranslateObjectsButton.label': '메쉬와 오브젝트들 번역',
    'TranslateObjectsButton.desc': '모든 메쉬와 오브젝트들을 내장된 사전과 구글번역을 이용해 영어로 번역합니다.',
    'TranslateObjectsButton.success': '{number}개의 메쉬들과 오브젝트들이 번역되었습니다.',

    'TranslateMaterialsButton.label': '매테리얼 번역',
    'TranslateMaterialsButton.desc': '모든 매테리얼들을 내장된 사전과 구글번역을 이용해 영어로 번역합니다.',
    'TranslateMaterialsButton.success': '{number}개의 매테리얼들이 번역되었습니다.',

    'TranslateTexturesButton.label': '텍스처 번역',
    'TranslateTexturesButton.desc': '모든 텍스처들을 내장된 사전과 구글번역을 이용해 영어로 번역합니다.',
    'TranslateTexturesButton.success_alt': '모든 텍스처들이 번역되었습니다.',
    'TranslateTexturesButton.error.noInternet': '구글에 연결하지 못했습니다. 인터넷 연결을 확인해주세요.',
    'TranslateTexturesButton.success': '{number}개의 텍스처들이 번역되었습니다',

    'TranslateAllButton.label': '모두 번역',
    'TranslateAllButton.desc': '모든 것들을 내장된 사전과 구글번역을 이용해 영어로 번역합니다.',
    'TranslateAllButton.success': '번역이 완료되었습니다.',

    'TranslateX.error.wrongVersion': '이 기능을 사용하려면 Blender 2.79 이상의 버전이 필요합니다.',

    'update_dictionary.error.cantConnect': '구글에 연결하지 못했습니다. 일부분은 번역되지 못했습니다.',
    'update_dictionary.error.temporaryBan': '일시적으로 Google 번역에서 차단 된 것 같습니다!',
    'update_dictionary.error.catsTranslated': '\nCats Plugin은 자체 내장된 로컬 사전으로 번역 할 수 있지만 나중에 Google 번역을 하려면 나중에 다시 시도해야합니다.',
    'update_dictionary.error.cantAccess': 'Cats는 Google 번역에 액세스 할 수 없습니다!',
    'update_dictionary.error.errorMsg': 'Google 번역에서 오류 메시지를 받았습니다!',
    'update_dictionary.error.apiChanged': 'Google 번역에서 번역을 가져올 수 없습니다!'
                                          '\n이는 Google이 API를 변경했으며 문제가 해결 될 때까지 번역이 더 이상 작동하지 않음을 의미합니다.'
                                          '\n수동으로 번역하거나 Cats 업데이트를 기다리십시오.'
                                          '\n업데이트 및 토론을 원하시면 Discord에 가입해주세요. 링크는 아래의 크레딧 패널에서 찾을 수 있습니다.',

    # Tools Viseme
    'AutoVisemeButton.label': '립싱크(Visemes) 생성',
    'AutoVisemeButton.desc': '당신의 아바타가 다양한 쉐이프키들을 조합하여 실제 음성을 모방하여 말하는 것처럼 보이게 합니다.\n'
                             '3개의 쉐이프키를 지정하여 새로운 15 종류의 쉐이프키들을 생성합니다.',
    'AutoVisemeButton.error.noShapekeys': '이 메쉬는 쉐이프키가 없습니다!',
    'AutoVisemeButton.error.selectShapekeys': '"Basis" 대신에 올바른 입모양 쉐이프키들을 선택하여 주세요!',
    'AutoVisemeButton.success': '입모양 쉐이프키들을 생성했습니다!',

    # Extensions
    'Scene.armature.label': '뼈대(Armature)',
    'Scene.armature.desc': 'Cats에서 쓰여질 뼈대(Armature)를 선택해주세요.',

    'Scene.zip_content.label': 'Zip Content',
    'Scene.zip_content.desc': '불러올 모델을 선택해주세요',

    'Scene.keep_upper_chest.label': 'Upper Chest 보존',
    'Scene.keep_upper_chest.desc': 'VRChat은 이제 상단 가슴(Upper Chest) 본을 부분적으로 지원하므로 더 이상 삭제할 필요가 없습니다.'
                                   '\n\n경고: 현재 이것은 눈 추적(Eye Tracking)을 망치기 때문에, 눈 추적을 원한다면 이것을 체크하지 말아주세요.',

    'Scene.combine_mats.label': '동일한 매테리얼 결합',
    'Scene.combine_mats.desc': '유사한 매테리얼들을 하나로 결합하여 드로우 콜을 줄입니다.\n\n'
                               '이 작업 후에도 아바타는 동일하게 보일 것입니다.\n'
                               '이것은 아바타를 최적화하는 데 매우 중요한 단계입니다.\n'
                               '이것에 문제가 있으면이 옵션을 선택 취소하고 우리에게 알려주세요!\n',

    'Scene.remove_zero_weight.label': '제로 웨이트 본들 제거',
    'Scene.remove_zero_weight.desc': '본 구조를 정리하고 어느 Vertex에도 영향을 주지 않는 모든 본들을 지웁니다.'
                                     '\n유지하려는 본들이나 버텍스 그룹이 지워질 경우 체크해제하세요',

    'Scene.keep_end_bones.label': '엔드 본들(End Bones) 유지',
    'Scene.keep_end_bones.desc': '엔드 본들을 유지합니다.'
                                 '\n\n다이나믹본을 사용하는 스커트의 움직임을 향상시키지만 본의 개수를 늘려버립니다.'
                                 '\n이것은 Unity에서 부서진 손가락 뼈들과 관련된 문제를 해결할 수도 있습니다.'
                                 '\n내보내기 할때는 언제나 "Add Leaf Bones"을 체크해제하거나 Cats의 내보내기(Export) 버튼을 사용하세요',

    'Scene.keep_twist_bones.label': '트위스트 본 유지',
    'Scene.keep_twist_bones.desc': '이름에 "Twist"가 들어간 본들을 유지합니다.'
                                   '\n따라서 유지하려는 특정 뼈가있는 경우 이름에 "Twist"를 추가 할 수 있으며 삭제되지 않습니다.'
                                   '\n\nVRChat은 이제 트위스트 본을 사용할 수 있으므로 이 옵션을 사용하여 유지할 수 있습니다.',

    'Scene.fix_twist_bones.label': 'MMD 트위스트 본 고치기',
    'Scene.fix_twist_bones.desc': 'VRChat에서 MMD 팔 트위스트 뼈대를 사용할 수 있습니다.'
                                  '\n트위스트 본의 이름이 올바르게 지정된 경우에만 작동합니다.'
                                  '\n필요한 이름형식:'
                                  '\n  - ArmTwist[1-3]_[L/R]'
                                  '\n  - HandTwist[1-3]_[L/R]'
                                  '\n\n이 작업을 위해 "Keep Twist Bones"를 활성화 할 필요가 없습니다.',

    'Scene.join_meshes.label': '메쉬 통합',
    'Scene.join_meshes.desc': '모델의 모든 메쉬들을 통합합니다.'
                            '\n또한:'
                            '\n  - 모든 쉐이프키들의 순서를 올바르게 재설정합니다.'
                            '\n  - 모든 변환(Transforms)을 적용'
                            '\n  - 망가진 아마추어 모디파이어들(armature modifiers)을 고침'
                            '\n  - 모든 데시메이션(decimation)과 미러 모디파이어들(mirror modifiers)을 적용'
                            '\n  - UV맵들을 올바르게 통합',
    'Scene.connect_bones.label': '본 연결',
    'Scene.connect_bones.desc': '모든 본들이 정확히 하나의 자식 본을 가지고 있다면 모든 본들을 그것들의 자식 본과 연결시켜줍니다.\n'
                                '뼈의 기능에는 영향을 주지 않으며 뼈대(armature)의 미관을 개선할 뿐입니다.',

    'Scene.fix_materials.label': '매테리얼 고치기',
    'Scene.fix_materials.desc': '매테리얼에 일부 VRChat 관련 픽스가 적용됩니다.',

    'Scene.remove_rigidbodies_joints.label': 'Rigidbodies와 Joints 제거',
    'Scene.remove_rigidbodies_joints.desc': 'Rigidbodies와 joints는 MMD software에서 물리연산을 위해 사용되는 것들입니다.'
                                            '\nVRChat에 사용되지않으므로 VRChat 유저들에게는 이것들을 지우는 게 좋습니다!',

    'Scene.use_google_only.label': '구버전 번역을 사용 (권장되지 않음)',
    'Scene.use_google_only.desc': '내장된 사전 대신에 구글 번역기를 쉐이프키 번역에 사용합니다.'
                                  '\n'
                                  '\n번역 속도가 느려지고 번역의 질이 더 나빠질 수 있지만, 번역은 CATS 0.9.0 버전 혹은 그 이전의 버전처럼 될 것이다.'
                                  '\n이전 번역에 의존하는 애니메이션을 새 번역으로 변환하지 않을 경우에만 이 기능을 사용하세요.',

    'Scene.show_more_options.label': '더 많은 옵션 보기',
    'Scene.show_more_options.desc': '더 많은 모델 옵션 보기',

    'Scene.merge_mode.label': '통합모드',
    'Scene.merge_mode.desc': 'Mode',
    'Scene.merge_mode.armature.label': '뼈대(Armatures) 통합',
    'Scene.merge_mode.armature.desc': 'Here you can merge two armatures together.',
    'Scene.merge_mode.mesh.label': 'Mesh 붙이기',
    'Scene.merge_mode.mesh.desc': 'Here you can attach a mesh to an armature.',

    'Scene.merge_armature_into.label': '기본 뼈대(Armature)',
    'Scene.merge_armature_into.desc': 'Select the armature into which the other armature will be merged\n',

    'Scene.merge_armature.label': '뼈대(Armature) 통합',
    'Scene.merge_armature.desc': 'Select the armature which will be merged into the selected armature above\n',

    'Scene.attach_to_bone.label': '본에 붙이기',
    'Scene.attach_to_bone.desc': 'Select the bone to which the armature will be attached to\n',

    'Scene.attach_mesh.label': '메쉬 붙이기',
    'Scene.attach_mesh.desc': 'Select the mesh which will be attached to the selected bone in the selected armature\n',

    'Scene.merge_same_bones.label': '모든 뼈 통합',
    'Scene.merge_same_bones.desc': 'Merges all bones together that have the same name instead of only the base bones (Hips, Spine, etc).'
                                   '\nYou will have to make sure that all the bones you want to merge have the same name.'
                                   '\n'
                                   '\nIf this is checked, you won\'t need to fix the model with CATS beforehand but it is still advised to do so.'
                                   '\nIf this is unchecked, CATS will only merge the base bones (Hips, Spine, etc).'
                                   '\n'
                                   '\nThis can have unintended side effects, so check your model afterwards!'
                                   '\n',

    'Scene.apply_transforms.label': '변환 적용',
    'Scene.apply_transforms.desc': 'Check this if both armatures and meshes are already at their correct positions.'
                                   '\nThis will cause them to stay exactly where they are when merging',

    'Scene.merge_armatures_join_meshes.label': '메쉬 통합',
    'Scene.merge_armatures_join_meshes.desc': 'This will join all meshes.'
                                              '\nNot checking this will always apply transforms',

    'Scene.merge_armatures_remove_zero_weight_bones.label': '제로웨이트 본 제거',
    'Scene.merge_armatures_remove_zero_weight_bones.desc': 'Cleans up the bones hierarchy, deleting all bones that don\'t directly affect any vertices.'
                                                           '\nUncheck this if bones or vertex groups that you want to keep got deleted',

    # Decimation
    'Scene.decimation_mode.label': 'Decimation Mode',
    'Scene.decimation_mode.desc': 'Decimation Mode',
    'Scene.decimation_mode.smart.label': "Smart",
    'Scene.decimation_mode.smart.desc': '최고의 결과 - 데시메이션 이후 쉐이프키들을 복구함\n'
                                        '\n'
                                        "This will decimate your whole model and attempt to undo the warping caused by Blender's decimation.\n"
                                        "This will give the best results and keep blinking and lip syncing, but may have issues on some models.",
    'Scene.decimation_mode.safe.label': '안전',
    'Scene.decimation_mode.safe.desc': '괜찮은 결과 - 쉐이프키 손실 없음\n'
                                       '\n'
                                       'This will only decimate meshes with no shape keys.\n'
                                       'The results are decent and you won\'t lose any shape keys.\n'
                                       'Eye Tracking and Lip Syncing will be fully preserved.',
    'Scene.decimation_mode.half.label': '반',
    'Scene.decimation_mode.half.desc': '나쁘지 않은 결과, - 최소한의 쉐이프키 손실됨\n'
                                       '\n'
                                       'This will only decimate meshes with less than 4 shape keys as those are often not used.\n'
                                       'The results are better but you will lose the shape keys in some meshes.\n'
                                       'Eye Tracking and Lip Syncing should still work.',
    'Scene.decimation_mode.full.label': '전체',
    'Scene.decimation_mode.full.desc': '일관된 결과 - 모든 쉐이프키들이 손실됨\n'
                                       '\n'
                                       'This will decimate your whole model deleting all shape keys in the process.\n'
                                       'This will give consistent results but you will lose the ability to add blinking and Lip Syncing.\n'
                                       'Eye Tracking will still work if you disable Eye Blinking.',
    'Scene.decimation_mode.custom.label': '커스텀',
    'Scene.decimation_mode.custom.desc': 'Custom results - custom shape key loss\n'
                                         '\n'
                                         'This will let you choose which meshes and shape keys should not be decimated.\n',

    'Scene.selection_mode.label': '선택 모드',
    'Scene.selection_mode.desc': 'Selection Mode',
    'Scene.selection_mode.shapekeys.label': '쉐이프키',
    'Scene.selection_mode.shapekeys.desc': 'Select all the shape keys you want to preserve here.',
    'Scene.selection_mode.meshes.label': '메쉬',
    'Scene.selection_mode.meshes.desc': 'Select all the meshes you don\'t want to decimate here.',

    'Scene.add_shape_key.label': '쉐이프키',
    'Scene.add_shape_key.desc': 'The shape key you want to keep',

    'Scene.add_mesh.label': '메쉬',
    'Scene.add_mesh.desc': 'The mesh you want to leave untouched by the decimation',

    'Scene.decimate_fingers.label': '손가락 살리기',
    'Scene.decimate_fingers.desc': 'Check this if you don\'t want to decimate your fingers!\n'
                                   'Results will be worse but there will be no issues with finger movement.\n'
                                   'This is probably only useful if you have a VR headset.\n'
                                   '\n'
                                   'This operation requires the finger bones to be named specifically:\n'
                                   'Thumb(0-2)_(L/R)\n'
                                   'IndexFinger(1-3)_(L/R)\n'
                                   'MiddleFinger(1-3)_(L/R)\n'
                                   'RingFinger(1-3)_(L/R)\n'
                                   'LittleFinger(1-3)_(L/R)',

    'Scene.decimate_hands.label': '손 살리기',
    'Scene.decimate_hands.desc': 'Check this if you don\'t want to decimate your full hands!\n'
                                 'Results will be worse but there will be no issues with hand movement.\n'
                                 'This is probably only useful if you have a VR headset.\n'
                                 '\n'
                                 'This operation requires the finger and hand bones to be named specifically:\n'
                                 'Left/Right wrist\n'
                                 'Thumb(0-2)_(L/R)\n'
                                 'IndexFinger(1-3)_(L/R)\n'
                                 'MiddleFinger(1-3)_(L/R)\n'
                                 'RingFinger(1-3)_(L/R)\n'
                                 'LittleFinger(1-3)_(L/R)',

    'Scene.decimation_remove_doubles.label': '이중 제거',
    'Scene.decimation_remove_doubles.desc': 'Uncheck this if you got issues with with this checked',
    'Scene.decimation_animation_weighting.label': "Animation weighting",
    'Scene.decimation_animation_weighting.desc': "Weight decimation based on shape keys and vertex group overlap\n"
                                                 "Results in better animating topology by trading off overall shape accuracy\n"
                                                 "Use if your elbows/joints end up with bad topology",
    'Scene.decimation_animation_weighting_factor.label': "Factor",
    'Scene.decimation_animation_weighting_factor.desc': "How much influence the animation weighting has on the overall shape",

    'Scene.max_tris.label': '삼각폴리곤(Tris)',
    'Scene.max_tris.desc': 'The target amount of tris after decimation',

    # Eye Tracking
    'Scene.eye_mode.label': 'Eye Mode',
    'Scene.eye_mode.desc': 'Mode',
    'Scene.eye_mode.creation.label': '생성',
    'Scene.eye_mode.creation.desc': 'Here you can create eye tracking.',
    'Scene.eye_mode.testing.label': '테스트',
    'Scene.eye_mode.testing.desc': 'Here you can test how eye tracking will look in-game.',

    'Scene.mesh_name_eye.label': '메쉬',
    'Scene.mesh_name_eye.desc': 'The mesh with the eyes vertex groups',

    'Scene.head.label': '머리',
    'Scene.head.desc': 'The head bone containing the eye bones',

    'Scene.eye_left.label': '왼쪽 눈',
    'Scene.eye_left.desc': 'The models left eye bone',

    'Scene.eye_right.label': '오른쪽 눈',
    'Scene.eye_right.desc': 'The models right eye bone',

    'Scene.wink_left.label': '왼쪽 깜빡임',
    'Scene.wink_left.desc': 'The shape key containing a blink with the left eye',

    'Scene.wink_right.label': '오른쪽 깜빡임',
    'Scene.wink_right.desc': 'The shape key containing a blink with the right eye',

    'Scene.lowerlid_left.label': '왼쪽 아래 눈꺼풀',
    'Scene.lowerlid_left.desc': 'The shape key containing a slightly raised left lower lid.\n'
                                'Can be set to "Basis" to disable lower lid movement',

    'Scene.lowerlid_right.label': '오른쪽 아래 눈꺼풀',
    'Scene.lowerlid_right.desc': 'The shape key containing a slightly raised right lower lid.\n'
                                 'Can be set to "Basis" to disable lower lid movement',

    'Scene.disable_eye_movement.label': '눈 움직임 비활성화',
    'Scene.disable_eye_movement.desc': 'IMPORTANT: Do your decimation first if you check this!\n'
                                       '\n'
                                       'Disables eye movement. Useful if you only want blinking.\n'
                                       'This creates eye bones with no movement bound to them.\n'
                                       'You still have to assign "LeftEye" and "RightEye" to the eyes in Unity',

    'Scene.disable_eye_blinking.label': '눈 깜빡임 비활성화',
    'Scene.disable_eye_blinking.desc': 'Disables eye blinking. Useful if you only want eye movement.\n'
                                       'This will create the necessary shape keys but leaves them empty',

    'Scene.eye_distance.label': '눈 움직임 범위',
    'Scene.eye_distance.desc': 'Higher = more eye movement\n'
                               'Lower = less eye movement\n'
                               'Warning: Too little or too much range can glitch the eyes.\n'
                               'Test your results in the "Eye Testing"-Tab!\n',

    'Scene.eye_rotation_x.label': '위 - 아래',
    'Scene.eye_rotation_x.desc': 'Rotate the eye bones on the vertical axis',

    'Scene.eye_rotation_y.label': '왼쪽 - 오른쪽',
    'Scene.eye_rotation_y.desc': 'Rotate the eye bones on the horizontal axis.'
                                 '\nThis is from your own point of view',

    'Scene.iris_height.label': '눈동자 높이',
    'Scene.iris_height.desc': 'Moves the iris away from the eye ball',

    'Scene.eye_blink_shape.label': '깜빡임 강도',
    'Scene.eye_blink_shape.desc': 'Test the blinking of the eye',

    'Scene.eye_lowerlid_shape.label': '아래 눈꺼풀 강도',
    'Scene.eye_lowerlid_shape.desc': 'Test the lowerlid blinking of the eye',

    'Scene.mesh_name_viseme.label': '메쉬',
    'Scene.mesh_name_viseme.desc': 'The mesh with the mouth shape keys',

    # Visemes
    'Scene.mouth_a.label': '발음 아(AA)',
    'Scene.mouth_a.desc': 'Shape key containing mouth movement that looks like someone is saying "aa".\nDo not put empty shape keys like "Basis" in here',

    'Scene.mouth_o.label': '발음 오(OH)',
    'Scene.mouth_o.desc': 'Shape key containing mouth movement that looks like someone is saying "oh".\nDo not put empty shape keys like "Basis" in here',

    'Scene.mouth_ch.label': '발음 츠(CH)',
    'Scene.mouth_ch.desc': 'Shape key containing mouth movement that looks like someone is saying "ch". Opened lips and clenched teeth.\nDo not put empty shape keys like "Basis" in here',

    'Scene.shape_intensity.label': '쉐이프키 혼합 강도',
    'Scene.shape_intensity.desc': 'Controls the strength in the creation of the shape keys. Lower for less mouth movement strength',

    # Bone Parenting
    'Scene.root_bone.label': '부모쪽으로',
    'Scene.root_bone.desc': 'List of bones that look like they could be parented together to a root bone',

    # Optimize
    'Scene.optimize_mode.label': '최적화 모드',
    'Scene.optimize_mode.desc': 'Mode',
    'Scene.optimize_mode.atlas.label': 'Atlas',
    'Scene.optimize_mode.atlas.desc': 'Allows you to make a texture atlas.',
    'Scene.optimize_mode.material.label': '매테리얼',
    'Scene.optimize_mode.material.desc': 'Some various options on material manipulation.',
    'Scene.optimize_mode.bonemerging.label': '본 통합',
    'Scene.optimize_mode.bonemerging.desc': 'Allows child bones to be merged into their parents.',

    # Bone Merging
    'Scene.merge_ratio.label': '통합 비율',
    'Scene.merge_ratio.desc': 'Higher = more bones will be merged\n'
                              'Lower = less bones will be merged\n',

    'Scene.merge_mesh.label': '메쉬',
    'Scene.merge_mesh.desc': 'The mesh with the bones vertex groups',

    'Scene.merge_bone.label': '통합할 부분',
    'Scene.merge_bone.desc': 'List of bones that look like they could be merged together to reduce overall bones',

    # Settings
    'Scene.show_mmd_tabs.label': 'mmd_tools 탭 보이기',
    'Scene.show_mmd_tabs.desc': 'Allows you to hide/show the mmd_tools tabs "MMD" and "Misc"',

    'Scene.embed_textures.label': '내보낼 때 텍스처 포함',
    'Scene.embed_textures.desc': 'Enable this to embed the texture files into the FBX file upon export.'
                                 '\nUnity will automatically extract these textures and put them into a separate folder.'
                                 '\nThis might not work for everyone and it increases the file size of the exported FBX file',

    'Scene.use_custom_mmd_tools.label': '커스텀 mmd_tools 사용',
    'Scene.use_custom_mmd_tools.desc': 'Enable this to use your own version of mmd_tools. This will disable the internal cats mmd_tools',

    'Scene.debug_translations.label': 'Google 번역 디버그',
    'Scene.debug_translations.desc': 'Tests the Google Translations and prints the Google response in case of error',

    # Bake
    'Scene.bake_resolution.label': "해상도",
    'Scene.bake_resolution.desc': "테스쳐들의 결과 해상도.\n"
                                  "- 2048 데스크탑 용\n"
                                  "- 1024 퀘스트 용",
    'Scene.bake_use_decimation.label': '축소(Decimate)',
    'Scene.bake_use_decimation.desc': '베이킹하기 전에 폴리 카운트를 줄인 다음 노멀 맵을 사용하여 디테일을 복원합니다.',
    'Scene.bake_generate_uvmap.label': 'UV 맵 생성',
    'Scene.bake_generate_uvmap.desc': "Re-pack islands for your mesh to a new non-overlapping UVMap.\n"
                                      "Only disable if your UVs are non-overlapping already.\n"
                                      "This will leave any map named \"Detail Map\" alone.\n"
                                      "Uses UVPackMaster where available for more efficient UVs, make sure the window is showing",
    'Scene.bake_uv_overlap_correction.label': "중복 보정",
    'Scene.bake_uv_overlap_correction.desc': "Method used to prevent overlaps in UVMap",
    'Scene.bake_prioritize_face.label': '머리 / 눈 우선 순위 지정',
    'Scene.bake_prioritize_face.desc': 'Scale any UV islands attached to the head/eyes by a given factor.',
    'Scene.bake_face_scale.label': "머리 / 눈 스케일",
    'Scene.bake_face_scale.desc': "How much to scale up the face/eyes portion of the textures.",
    'Scene.bake_quick_compare.label': '빠른 비교',
    'Scene.bake_quick_compare.desc': 'Move output avatar next to existing one to quickly compare',
    'Scene.bake_illuminate_eyes.label': '눈을 최대 밝기로 설정',
    'Scene.bake_illuminate_eyes.desc': 'Relight LeftEye and RightEye to be full brightness.\n'
                                       "Without this, the eyes will have the shadow of the surrounding socket baked in,\n"
                                       "which doesn't animate well",
    'Scene.bake_pass_smoothness.label': '부드러움',
    'Scene.bake_pass_smoothness.desc': 'Bakes Roughness and then inverts the values.\n'
                                       'To use this, it needs to be packed to the Alpha channel of either Diffuse or Metallic.\n'
                                       'Not neccesary if your mesh has a global roughness value',
    'Scene.bake_pass_diffuse.label': '확산 (색상)',
    'Scene.bake_pass_diffuse.desc': 'Bakes diffuse, un-lighted color. Usually you will want this.\n'
                                    'While baking, this temporarily links "Metallic" to "Anisotropic Rotation" as metallic can cause issues.',
    'Scene.bake_preserve_seams.label': "이음새 유지",
    'Scene.bake_preserve_seams.desc': 'Forces the Decimate operation to preserve vertices making up seams, preventing hard edges along seams.\n'
                                      'May result in less ideal geometry.\n'
                                      "Use if you notice ugly edges along your texture seams.",
    'Scene.bake_pass_normal.label': '노말 (범프)',
    'Scene.bake_pass_normal.desc': "Bakes a normal (bump) map. Allows you to keep the shading of a complex object with\n"
                                   "the geometry of a simple object. If you have selected 'Decimate', it will create a map\n"
                                   "that makes the low res output look like the high res input.\n"
                                   "Will not work well if you have self-intersecting islands",
    'Scene.bake_normal_apply_trans.label': '변환 적용',
    'Scene.bake_normal_apply_trans.desc': "Applies offsets while baking normals. Neccesary if your model has many materials with different normal maps\n"
                                          "Turn this off if applying location causes problems with your model",
    'Scene.bake_pass_ao.label': 'Ambient Occlusion',
    'Scene.bake_pass_ao.desc': 'Bakes Ambient Occlusion, non-projected shadows. Adds a significant amount of detail to your model.\n'
                               'Reccomended for non-toon style avatars.\n'
                               'Takes a fairly long time to bake',
    'Scene.bake_pass_questdiffuse.label': 'Quest Diffuse (Color+AO)',
    'Scene.bake_pass_questdiffuse.desc': 'Blends the result of the Diffuse and AO bakes to make Quest-compatible shading.',
    'Scene.bake_pass_emit.label': 'Emit',
    'Scene.bake_pass_emit.desc': 'Bakes Emit, glowyness',
    'Scene.bake_diffuse_alpha_pack.label': "Alpha Channel",
    'Scene.bake_diffuse_alpha_pack.desc': "What to pack to the Diffuse Alpha channel",
    'Scene.bake_metallic_alpha_pack.label': "Metallic Alpha Channel",
    'Scene.bake_metallic_alpha_pack.desc': "What to pack to the Metallic Alpha channel",
    'Scene.bake_pass_alpha.label': 'Transparency',
    'Scene.bake_pass_alpha.desc': 'Bakes transparency by connecting the last Principled BSDF Alpha input\n'
                                  'to the Base Color input and baking Diffuse.\n'
                                  'Not a native pass in Blender, results may vary\n'
                                  'Unused if you are baking to Quest',
    'Scene.bake_pass_metallic.label': 'Metallic',
    'Scene.bake_pass_metallic.desc': 'Bakes metallic by connecting the last Principled BSDF Metallic input\n'
                                     'to the Base Color input and baking Diffuse.\n'
                                     'Not a native pass in Blender, results may vary',
    'Scene.bake_questdiffuse_opacity.label': "AO Opacity",
    'Scene.bake_questdiffuse_opacity.desc': "The opacity of the shadows to blend onto the Diffuse map.\n"
                                            "This should match the unity slider for AO on the Desktop version.",

    "Scene.bake_uv_overlap_correction.none.label": "None",
    "Scene.bake_uv_overlap_correction.none.desc": "Leave islands as they are. Use if islands don't self-intersect at all",
    "Scene.bake_uv_overlap_correction.unmirror.label": "Unmirror",
    "Scene.bake_uv_overlap_correction.unmirror.desc": "Move all face islands with positive X values over one to un-pin mirrored UVs. Solves most UV pinning issues.",
    "Scene.bake_uv_overlap_correction.reproject.label": "Reproject",
    "Scene.bake_uv_overlap_correction.reproject.desc": "Use blender's Smart UV Project to come up with an entirely new island layout. Tends to reduce quality.",

    "Scene.bake_diffuse_alpha_pack.none.label": "None",
    "Scene.bake_diffuse_alpha_pack.none.desc": "No alpha channel",
    "Scene.bake_diffuse_alpha_pack.transparency.label": "Transparency",
    "Scene.bake_diffuse_alpha_pack.transparency.desc": "Pack Transparency",
    "Scene.bake_diffuse_alpha_pack.smoothness.label": "Smoothness",
    "Scene.bake_diffuse_alpha_pack.smoothness.desc": "Pack Smoothness. Most efficient if you don't have transparency or metallic textures.",

    "Scene.bake_metallic_alpha_pack.none.label": "None",
    "Scene.bake_metallic_alpha_pack.none.desc": "No alpha channel",
    "Scene.bake_metallic_alpha_pack.smoothness.label": "Smoothness",
    "Scene.bake_metallic_alpha_pack.smoothness.desc": "Pack Smoothness. Use this if your Diffuse alpha channel is already populated with Transparency",

    "cats_bake.warn_missing_nodes": "A material in use isn't using Nodes, fix this in the Shading tab.",
    "cats_bake.preset_desktop.label": "Desktop",
    "cats_bake.preset_desktop.desc": "Preset for producing an Excellent-rated Desktop avatar, not accounting for bones.\n"
                                     "This will try to automatically detect which bake passes are relevant to your model",
    "cats_bake.preset_quest.label": 'Quest',
    "cats_bake.preset_quest.desc": "Preset for producing an Excellent-rated Quest avatar, not accounting for bones.\n"
                                   "This will try to automatically detect which bake passes are relevant to your model",
    'cats_bake.bake.label': 'Copy and Bake (SLOW!)',
    'cats_bake.bake.desc': "Perform the bake. Warning, this performs an actual render!\n"
                           "This will create a copy of your avatar to leave the original alone.\n"
                           "Depending on your machine and model, this could take an hour or more.\n"
                           "For each pass, any Value node in your materials labeled bake_<bakename> will be\n"
                           "set to 1.0, for more granular customization.",
    'cats_bake.error.no_meshes': "메쉬가 발견되지 않음!",
    'cats_bake.error.render_engine': "You need to set your render engine to Cycles first!",
    'cats_bake.error.render_disabled': "One or more of your armature's meshes have rendering disabled!",
    'cats_bake.info.success': "Success! Textures and model saved to \'CATS Bake\' folder next to your .blend file.",

    'cats_bake.tutorial_button.label': "사용법",
    'cats_bake.tutorial_button.desc': "This will open the Cats wiki page for the Bake panel",
    'cats_bake.tutorial_button.URL': "https://github.com/GiveMeAllYourCats/cats-blender-plugin/wiki/Bake",
    'cats_bake.tutorial_button.success': "Bake Tutorial opened.",

    # Updater
    'CheckForUpdateButton.label': '업데이트 체크',
    'CheckForUpdateButton.desc': 'Checks if a new update is available for CATS',

    'UpdateToLatestButton.label': '지금 업데이트',
    'UpdateToLatestButton.desc': 'Update CATS to the latest version',

    'UpdateToSelectedButton.label': '선택된 버전으로 업데이트',
    'UpdateToSelectedButton.desc': 'Update CATS to the selected version',

    'UpdateToDevButton.label': '개발버전으로 업데이트',
    'UpdateToDevButton.desc': 'Update CATS to the Development version',

    'RemindMeLaterButton.label': '나중에 다시보기',
    'RemindMeLaterButton.desc': 'This hides the update notification \'til the next Blender restart',
    'RemindMeLaterButton.success': 'You will be reminded later',

    'IgnoreThisVersionButton.label': '이 버전은 무시하기',
    'IgnoreThisVersionButton.desc': 'This ignores this version. You will be reminded again when the next version releases',
    'IgnoreThisVersionButton.success': 'Version {name} will be ignored.',

    'ShowPatchnotesPanel.label': '패치노트',
    'ShowPatchnotesPanel.desc': 'Shows the patchnotes of the selected version',
    'ShowPatchnotesPanel.releaseDate': 'Released: {date}',

    'ConfirmUpdatePanel.label': '업데이트 확인',
    'ConfirmUpdatePanel.desc': 'This shows you a panel in which you have to confirm your update choice',
    'ConfirmUpdatePanel.warn.dev1': 'Warning:',
    'ConfirmUpdatePanel.warn.dev2': ' The development version of CATS if the place where',
    'ConfirmUpdatePanel.warn.dev3': ' we test new features and bug fixes.',
    'ConfirmUpdatePanel.warn.dev4': ' This version might be very unstable and some features',
    'ConfirmUpdatePanel.warn.dev5': ' might not work correctly.',
    'ConfirmUpdatePanel.ShowPatchnotesPanel.label': '패치노트 보기',
    'ConfirmUpdatePanel.updateNow': 'Update now:',

    'UpdateCompletePanel.label': '설치 보고',
    'UpdateCompletePanel.desc': 'The update is now complete',
    'UpdateCompletePanel.success1': 'CATS was successfully updated.',
    'UpdateCompletePanel.success2': 'Restart Blender to complete the update.',
    'UpdateCompletePanel.failure1': 'Update failed.',
    'UpdateCompletePanel.failure2': 'See Updater Panel for more info.',

    'UpdateNotificationPopup.label': '업데이트 가능',
    'UpdateNotificationPopup.desc': 'This shows you that an update is available',
    'UpdateNotificationPopup.newUpdate': 'CATS v{name} available!',
    'UpdateNotificationPopup.ShowPatchnotesPanel.label': '패치노트 보기',

    'check_for_update.cantCheck': 'Could not check for updates, try again later',

    'download_file.cantConnect': 'Could not connect to Github',
    'download_file.cantFindZip': 'Could not find the downloaded zip',
    'download_file.cantFindCATS': 'Could not find CATS in the downloaded zip',

    'draw_update_notification_panel.success': 'Restart Blender to complete update!',
    'draw_update_notification_panel.newUpdate': 'CATS v{name} available!',
    'draw_update_notification_panel.UpdateToLatestButton.label': '지금 업데이트',
    'draw_update_notification_panel.RemindMeLaterButton.label': '나중에 다시보기',
    'draw_update_notification_panel.IgnoreThisVersionButton.label': '이 버전은 무시하기',

    'draw_updater_panel.updateLabel': 'Updates:',
    'draw_updater_panel.updateLabel_alt': 'CATS Updater:',
    'draw_updater_panel.success': 'Restart Blender to complete update!',
    'draw_updater_panel.CheckForUpdateButton.label': '확인 중..',
    'draw_updater_panel.UpdateToLatestButton.label': '{name}로 업데이트',
    'draw_updater_panel.CheckForUpdateButton.label_alt': 'Check now for Update',
    'draw_updater_panel.UpdateToLatestButton.label_alt': 'Up to Date!',
    'draw_updater_panel.UpdateToSelectedButton.label': '설치버전:',
    'draw_updater_panel.UpdateToDevButton.label': '개발버전 설치',
    'draw_updater_panel.currentVersion': 'Current version: {name}',

    'bpy.types.Scene.cats_updater_version_list.label': '버전',
    'bpy.types.Scene.cats_updater_version_list.desc': 'Select the version you want to install\n',

    'bpy.types.Scene.cats_update_action.label': '액션 선택',
    'bpy.types.Scene.cats_update_action.desc': 'Action',
    'bpy.types.Scene.cats_update_action.update.label': '지금 업데이트',
    'bpy.types.Scene.cats_update_action.update.desc': 'Updates now to the latest version',
    'bpy.types.Scene.cats_update_action.ignore.label': '이 버전은 무시하기',
    'bpy.types.Scene.cats_update_action.ignore.desc': 'This ignores this version. You will be reminded again when the next version releases',
    'bpy.types.Scene.cats_update_action.defer.label': '나중에 다시보기',
    'bpy.types.Scene.cats_update_action.defer.desc': 'Hides the update notification til the next Blender restart',

}