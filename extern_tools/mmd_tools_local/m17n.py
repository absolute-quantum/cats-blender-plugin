# -*- coding: utf-8 -*-

translation_dict = {
    "ja_JP": {
        # Preferences
        ("*", "View3D > Sidebar > MMD Tools Panel"): "3Dビュー > サイドバー > MMD Toolsパネル",
        ("*", "Utility tools for MMD model editing. (UuuNyaa's forked version)"): "MMDモデル編集用のユーティリティーツールです。(UuuNyaaのフォーク版)",
        ("*", "Enable MMD Model Production Features"): "MMDモデル製作機能を有効化",
        ("*", "Shared Toon Texture Folder"): "共有トゥーンテクスチャフォルダ",
        ("*", "Base Texture Folder"): "ベーステクスチャフォルダ",
        ("*", "Dictionary Folder"): "辞書フォルダ",
        ("*", "Non-Collision Threshold"): "非コリジョンしきい値",

        ("*", "Add-on update"): "アドオン更新",
        ("Operator", "Restart Blender to complete update"): "Blenderを再起動して更新を完了",
        ("Operator", "Check mmd_tools add-on update"): "mmd_toolsアドオンの更新を確認",
        ("*", "Update to the latest release version ({})"): "最新バージョンへ更新",
        ("Operator", "No updates are available"): "更新はありません",
        ("*", "(Danger) Manual Update:"): "(危険)手動更新:",
        ("*", "Branch"): "ブランチ",
        ("*", "Target"): "ターゲット",
        ("Operator", "Update"): "更新",

        ("*", "Failed to check update {}. ({})"): "更新の確認に失敗しました。{} ({})",
        ("*", "Checked update. ({})"): "更新を確認しました。({})",
        ("*", "Updated to {}. ({})"): "{}へ更新しました。({})",
        ("*", "Failed to update {}. ({})"): "更新に失敗しました。{} ({})",

        # 3D Viewport > Sidebar > MMD > Model Production
        ("*", "Model Production"): "モデル製作",
        ("Operator", "Create Model"): "モデルを作成",
        ("Operator", "Create a MMD Model Root Object"): "MMDモデルルートオブジェクトを作成",
        ("*", "Name(Eng)"): "名前(英語)",

        ("Operator", "Convert Model"): "モデルを変換",
        ("Operator", "Convert to a MMD Model"): "MMDモデルへ変換",
        ("*", "Ambient Color Source"): "アンビエントカラーソース",
        ("*", "Edge Threshold"): "輪郭しきい値",
        ("*", "Minimum Edge Alpha"): "最小輪郭アルファ",
        ("*", "Convert Material Nodes"): "マテリアルノードを変換",
        ("*", "Middle Joint Bones Lock"): "中間関節ボーンをロック",

        ("Operator", "Attach Meshes"): "メッシュを取付",

        ("Operator", "Translate"): "翻訳",
        ("Operator", "Translate a MMD Model"): "MMDモデルを翻訳",
        ("Operator", "(Experimental) Global Translation"): "(実験的) 全体翻訳",
        ("*", "Dictionary"): "辞書",
        ("*", "Modes"): "モード",
        ("*", "MMD Names"): "MMD名",
        ("*", "Blender Names"): "Blender名",
        ("*", "Use Morph Prefix"): "モーフ接頭辞を使用",
        ("*", "Allow Fails"): "失敗を許可",

        ("*", "Model Surgery:"): "モデル手術",
        ("Operator", "Chop"): "切断",
        ("Operator", "Peel"): "はがす",
        ("Operator", "Model Separate by Bones"): "モデルをボーンで分離",
        ("*", "Separate Armature"): "アーマチュアを分離する",
        ("*", "Include Descendant Bones"): "子孫ボーンを含む",
        ("*", "Weight Threshold"): "ウェイトしきい値",
        ("*", "Boundary Joint Owner"): "境界ジョイントオーナー",
        ("*", "Source Model"): "分離元モデル",
        ("*", "Destination Model"): "分離先モデル",

        ("Operator", "Join"): "統合",
        ("Operator", "Model Join by Bones"): "モデルをボーンで統合",
        ("*", "Join Type"): "接続タイプ",

        # 3D Viewport > Sidebar > MMD > Model Setup
        ("*", "Model Setup"): "モデル設定",
        ("*", "Visibility:"): "可視性:",
        ("*", "Assembly:"): "組み立て:",
        ("Operator", "Physics"): "物理演算",
        ("Operator", "Build Rig"): "ビルドリグ",
        ("*", "Non-Collision Distance Scale"): "非衝突距離スケール",
        ("*", "Collision Margin"): "衝突マージン",

        ("Operator", "SDEF"): "SDEF",
        ("Operator", "Bind SDEF Driver"): "SDEFドライバーをバインド",
        ("*", "- Auto -"): "自動",
        ("*", "Bulk"): "バルク",
        ("*", "Skip"): "スキップ",

        ("*", "IK Toggle:"): "IK切替え:",

        ("*", "Mesh:"): "メッシュ:",
        ("Operator", "Separate by Materials"): "マテリアルで分解",
        ("Operator", "Join"): "統合",
        ("*", "Sort Shape Keys"): "シェイプキーをソート",

        ("*", "Material:"): "マテリアル:",
        ("Operator", "Edge Preview"): "輪郭プレビュー",
        ("Operator", "Convert to Blender"): "Blender用に変換",
        ("Operator", "Convert Materials"): "マテリアルを変換",
        ("*", "Convert to Principled BSDF"): "プリンシプルBSDFへ変換",
        ("*", "Clean Nodes"): "ノードをクリーン",

        ("*", "Misc:"): "その他:",

        # 3D Viewport > Sidebar > MMD > Scene Setup
        ("*", "Scene Setup"): "シーン設定",
        ("Operator", "MMD Tools/Manual"): "MMD Tools/マニュアル",
        ("Operator", "Import"): "インポート",
        ("Operator", "Export"): "エクスポート",

        ("*", "Model:"): "モデル:",
        ("*", "Types"): "タイプ",
        ("*", "Morphs"): "モーフ",
        ("*", "Clean Model"): "モデルをクリーン",
        ("*", "Fix IK Links"): "IKリンクを修正",
        ("*", "Apply Bone Fixed Axis"): "ボーン修正回転軸を適用",
        ("*", "Rename Bones - L / R Suffix"): "ボーンをリネーム - L / R接尾辞",
        ("*", "Rename Bones - Use Underscore"): "ボーンをリネーム - アンダースコア使用",
        ("*", "Rename Bones To English"): "ボーンを英語にリネーム",
        ("*", "Internal Dictionary"): "内蔵辞書",
        ("*", "use MIP maps for UV textures"): "UVテクスチャへミップマップを使用",
        ("*", "influence of .sph textures"): ".sphテクスチャの影響度",
        ("*", "influence of .spa textures"): ".spaテクスチャの影響度",
        ("*", "Log level"): "ログレベル",
        ("*", "Create a log file"): "ログファイルを作成",
        ("*", "Copy textures"): "テクスチャをコピー",
        ("*", "Sort Materials"): "マテリアルをソート",
        ("*", "Disable SPH/SPA"): "SPH/SPAを無効化",
        ("*", "Visible Meshes Only"): "可視メッシュのみ",
        ("*", "Overwrite Bone Morphs"): "ボーンモーフを上書き",
        ("*", "Overwrite the bone morphs from active pose library before exporting."): "エクスポート前にボーンモーフをアクティブなポーズライブラリから上書きします。",
        ("*", "(Experimental) Translate in Presets"): "(実験的) プリセットで翻訳",
        ("*", "Translate in presets before exporting."): "エクスポート前にプリセットで翻訳します。",
        ("*", "Sort Vertices"): "頂点をソート",

        ("*", "Motion:"): "モーション:",
        ("*", "Bone Mapper"): "ボーンマッパー",
        ("*", "Renamed bones"): "リネームしたボーン",
        ("*", "Treat Current Pose as Rest Pose"): "現在のポーズをレストポーズとして処理",
        ("*", "Mirror Motion"): "モーションをミラー",
        ("*", "Update scene settings"): "シーン設定を更新",
        ("*", "Use Frame Range"): "フレーム範囲を使用",
        ("*", "Use NLA"): "NLAを使用",

        ("*", "Pose:"): "ポーズ:",
        ("*", "Current Pose"): "現在のポーズ",
        ("*", "Active Pose"): "アクティブなポーズ",
        ("*", "All Poses"): "全てのポーズ",

        ("*", "Timeline:"): "タイムライン:",

        ("*", "Rigid Body Physics:"): "リジッドボディ物理演算:",
        ("Operator", "Update World"): "ワールドを更新",
        ("*", "Substeps"): "サブステップ",
        ("*", "Iterations"): "反復数",

        # 3D Viewport > Sidebar > MMD > Display Panel
        ("*", "Display Panel"): "表示パネル",
        ("Operator", "Bone"): "ボーン",
        ("Operator", "Morph"): "モーフ",
        ("Operator", "Add Display Item Frame"): "表示項目フレームを追加",
        ("Operator", "Remove Display Item Frame"): "表示項目フレームを削除",
        ("Operator", "Move Display Item Frame"): "表示項目フレームを移動",
        ("Operator", "Add Display Item"): "表示項目を追加",
        ("Operator", "Remove Display Item"): "表示項目を削除",
        ("Operator", "Move Display Item"): "表示項目を移動",
        ("*", "Quick setup display items"): "表示項目のクイックセットアップ",
        ("*", "Load Facial Items"): "表情項目をロード",
        ("*", "Load Bone Groups"): "ボーングループをロード",
        ("*", "Apply Bone Groups"): "ボーングループを適用",
        ("Operator", "Move To Top"): "最初へ移動",
        ("Operator", "Move To Bottom"): "最後へ移動",
        ("Operator", "Delete All"): "全て削除",

        # 3D Viewport > Sidebar > MMD > Morph Tools Panel
        ("*", "Morph Tools"): "モーフツール",
        ("*", "Eye"): "目",
        ("*", "Eye Brow"): "眉毛",
        ("*", "Mouth"): "口",
        ("Operator", "Add Morph"): "モーフを追加",
        ("Operator", "Remove Morph"): "モーフを削除",
        ("Operator", "Copy Morph"): "モーフをコピー",
        ("Operator", "Overwrite Bone Morphs from active Pose Library"): "ボーンモーフをアクティブなポーズライブラリから上書き",
        ("Operator", "Move Morph"): "モーフを移動",
        ("Operator", "Add Morph Offset"): "モーフオフセットを追加",
        ("Operator", "Remove Morph Offset"): "モーフオフセットを削除",
        ("*", "Related Mesh"): "関連するメッシュ",
        ("Operator", "Create Work Material"): "ワークマテリアルを生成",
        ("Operator", "Init Material Offset"): "マテリアルオフセットを初期化",
        ("*", "Texture factor"): "テクスチャ係数",
        ("*", "Sphere Texture factor"): "スフィアテクスチャ係数",
        ("*", "Toon Texture factor"): "トゥーンテクスチャ係数",

        # 3D Viewport > Sidebar > MMD > Rigid Bodies
        ("*", "Rigid Bodies"): "リジッドボディ",
        ("*", "Active Model"): "選択中のモデル",
        ("*", "All Models"): "全てのモデル",
        ("Operator", "Select Similar..."): "類似を選択...",
        ("Operator", "Select Rigid Body"): "リジッドボディを選択",
        ("*", "Collision Group"): "コリジョングループ",
        ("*", "Collision Group Mask"): "コリジョングループマスク",
        ("*", "Rigid Type"): "リジッドタイプ",
        ("*", "Hide Others"): "他を隠す",

        # 3D Viewport > Sidebar > MMD > Joints
        ("*", "Joints"): "ジョイント",
        ("Operator", "Add Joint"): "ジョイントを追加",
        ("Operator", "Remove Joint"): "ジョイントを削除",

        # 3D Viewport > Sidebar > MMD > Material Sorter Panel
        ("*", "Material Sorter"): "マテリアル順序",
        ("*", "Select a mesh object"): "メッシュを選択してください",
        ("*", "Use the arrows to sort"): "矢印を使って並べ替えてください",
        ("Operator", "Move Material Up"): "マテリアルを移動",
        ("Operator", "Move Material Down"): "マテリアルを移動",

        # 3D Viewport > Sidebar > MMD > Meshes Sorter Panel
        ("*", "Meshes Sorter"): "メッシュ順序",
        ("*", "Select a MMD Model"): "MMDモデルを選択してください",
        ("Operator", "Move Object"): "オブジェクトを移動",

        # 3D Viewport > Sidebar > MMD > Bone Order Panel
        ("*", "Bone Order"): "ボーン順序",
        ("*", "After Dynamics"): "物理後",
        ("*", "Transform Order"): "変形階層",

        # 3D Viewport > Sidebar > Misc > MMD Display Panel
        ("*", "MMD Display"): "MMD表示",
        ("*", "Temporary Object"): "テンポラリオブジェクト",
        ("*", "Rigid Body Name"): "リジッドボティ名",
        ("*", "Joint"): "ジョイント",
        ("*", "Joint Name"): "ジョイント名",
        ("*", "Toon Texture"): "トゥーンテクスチャ",
        ("*", "Sphere Texture"): "スフィアテクスチャ",
        ("*", "Property Drivers"): "プロパティドライバー",

        # 3D Viewport > Shading
        ("*", "MMD Shading Presets"): "MMDシェーディングプリセット",
        ("Operator", "Shadeless"): "影なし",

        # 3D Viewport > Menu > Object
        ("Operator", "Clean Shape Keys"): "シェイプキーをクリーン",

        # 3D Viewport > Menu > Pose
        ("Operator", "MMD Flip Pose"): "MMDポーズを反転",

        # 3D Viewport > Menu > Select
        ("Operator", "Select MMD Rigid Body"): "MMDリジッドボディ選択",

        # Properties > Object Properties > MMD Light Tools
        ("*", "MMD Light Tools"): "MMDライトツール",
        ("Operator", "Convert to MMD Light"): "MMDライトへ変換",
        ("*", "Light Source"): "光源",

        # Properties > Object Properties > MMD Camera Tools
        ("*", "MMD Camera Tools"): "MMDカメラツール",
        ("Operator", "Convert to MMD Camera"): "MMDカメラへ変換",
        ("*", "Camera Source"): "カメラソース",

        # Properties > Object Properties > MMD Model Information Panel
        ("*", "MMD Model Information"): "MMDモデル情報",
        ("*", "Name (English)"): "名前(英語)",
        ("*", "Comment (English)"): "コメント(英語)",
        ("Operator", "Change MMD IK Loop Factor"): "MMD IK反復係数を変更",
        ("*", "MMD IK Loop Factor"): "MMD IK反復係数",
        ("Operator", "Recalculate bone roll"): "ボーンロールを再計算",
        ("*", "This operation will break existing f-curve/action."): "この操作は既存のFカーブ/アクションを破壊します。",
        ("*", "Click [OK] to run the operation."): "[OK]をクリックして操作を実行してください。",

        # Properties > Object Properties > MMD Rigid Body
        ("*", "MMD Rigid Body"): "MMDリジッドボディ",
        ("*", "Physics + Bone"): "物理演算 + ボーン",
        ("*", "Collision Group Mask:"): "コリジョングループマスク:",

        # Properties > Object Properties > MMD Joint
        ("*", "MMD Joint"): "MMDジョイント",
        ("*", "X-Axis:"): "X軸:",
        ("*", "Y-Axis:"): "Y軸:",
        ("*", "Z-Axis:"): "Z軸:",
        ("*", "Spring(Linear)"): "スプリング(リニア)",
        ("*", "Spring(Angular)"): "スプリング(角度)",

        # Properties > Material Properties > MMD Material Panel
        ("*", "MMD Material"): "MMDマテリアル",
        ("*", "Color:"): "カラー:",
        ("*", "Shadow:"): "シャドウ:",
        ("*", "Double Sided"): "両面表示",
        ("*", "Ground Shadow"): "地面シャドウ",
        ("*", "Self Shadow Map"): "セルフシャドウマップ",
        ("*", "Self Shadow"): "セルフシャドウ",
        ("*", "Toon Edge"): "トゥーン輪郭",
        ("*", "Edge Color"): "輪郭カラー",
        ("*", "Edge Weight"): "輪郭ウェイト",

        # Properties > Material Properties > MMD Texture Panel
        ("*", "MMD Texture"): "MMDテクスチャ",
        ("*", "Texture:"): "テクスチャ:",
        ("*", "Sphere Texture:"): "スフィアテクスチャ:",
        ("*", "SubTexture"): "サブテクスチャ",
        ("*", "Use Shared Toon Texture"): "共有トゥーンテクスチャを使用",
        ("*", "Shared Toon Texture"): "共有トゥーンテクスチャ",

        # Properties > Bone Properties > MMD Bone Tools Panel
        ("*", "MMD Bone Tools"): "MMDボーンツール",
        ("*", "Information:"): "情報:",
        ("*", "Controllable"): "操作",
        ("*", "Tip Bone"): "ティップボーン",
        ("*", "Fixed Axis"): "軸制限",
        ("*", "Local Axes"): "ローカル軸",
        ("*", "Local X-Axis"): "ローカルX軸",
        ("*", "Local Z-Axis"): "ローカルZ軸",
        ("*", "Rotate +"): "回転 +",
        ("*", "Move +"): "移動 +",

        # Shader Editor > Shader Nodes
        ("*", "Base Tex Fac"): "ベーステクスチャ係数",
        ("*", "Base Tex"): "ベーステクスチャ",
        ("*", "Base Alpha"): "ベースアルファ",
        ("*", "Base UV"): "ベースUV",
        ("*", "Toon Tex Fac"): "トゥーンテクスチャ係数",
        ("*", "Toon Tex"): "トゥーンテクスチャ",
        ("*", "Toon Alpha"): "トゥーンアルファ",
        ("*", "Toon UV"): "トゥーンUV",
        ("*", "Sphere Tex Fac"): "スフィアテクスチャ係数",
        ("*", "Sphere Tex"): "スフィアテクスチャ",
        ("*", "Sphere Alpha"): "スフィアアルファ",
        ("*", "Sphere UV"): "スフィアUV",
        ("*", "Sphere Mul/Add"): "スフィア 乗算/加算",
        ("*", "SubTex UV"): "サブテクスチャUV",

        # Operator Popup > Global Translation Popup
        ("Operator", "Global Translation Popup"): "全体翻訳ポップアップ",
        ("*", "is Blank:"): "空白のみ:",
        ("*", "Japanese"): "日本語",
        ("*", "English"): "英語",
        ("*", "Select the target column for Batch Operations:"): "一括操作の対象列を選択:",
        ("*", "Blender Name (name)"): "Blender名称 (name)",
        ("*", "Japanese MMD Name (name_j)"): "日本語MMD名称 (name_j)",
        ("*", "English MMD Name (name_e)"): "英語MMD名称 (name_e)",
        ("*", "Batch Operation:"): "一括操作:",
        ("*", "Clear"): "クリア",
        ("*", "Translate to English"): "英語へ翻訳",
        ("*", "Blender L/R to MMD L/R"): "Blenderの左右をMMDの左右へ",
        ("*", "MMD L/R to Blender L/R"): "MMDの左右をBlenderの左右へ",
        ("*", "Restore Blender Names"): "Blender名称を復元",
        ("*", "Restore Japanese MMD Names"): "日本語MMD名称を復元",
        ("*", "Restore English MMD Names"): "英語MMD名称を復元",
        ("*", "Copy English MMD Names, if empty copy Japanese MMD Name"): "英語MMD名称をコピー、空なら日本語MMD名称をコピー",
        ("*", "Copy Japanese MMD Names, if empty copy English MMD Name"): "日本語MMD名称をコピー、空なら英語MMD名称をコピー",
        ("Operator", "Execute"): "実行",
        ("*", "Dictionaries:"): "辞書:",
    },
    "zh_CN": {
        # Preferences
        ("*", "View3D > Sidebar > MMD Tools Panel"): "3D视图 > 侧栏 > MMD Tools面板",
        ("*", "Utility tools for MMD model editing. (UuuNyaa's forked version)"): "用于MMD模型编辑的实用工具。(UuuNyaa的分叉版本)",
        ("*", "Enable MMD Model Production Features"): "开启MMD模型生产功能",
        ("*", "Shared Toon Texture Folder"): "共用的卡通纹理文件夹",
        ("*", "Base Texture Folder"): "基线纹理文件夹",
        ("*", "Dictionary Folder"): "辞書文件夹",
        ("*", "Non-Collision Threshold"): "非碰撞阈值",

        ("*", "Add-on update"): "插件更新",
        ("Operator", "Restart Blender to complete update"): "重新启动Blender以完成更新",
        ("Operator", "Check mmd_tools add-on update"): "检查mmd_tools插件更新",
        ("*", "Update to the latest release version ({})"): "更新到最新发布版本",
        ("Operator", "No updates are available"): "没有更新",
        ("*", "(Danger) Manual Update:"): "(危险)手动更新:",
        ("*", "Branch"): "分支",
        ("*", "Target"): "目标",
        ("Operator", "Update"): "更新",

        ("*", "Failed to check update {}. ({})"): "更新の確認に失敗しました。{} ({})",
        ("*", "Checked update. ({})"): "更新を確認しました。({})",
        ("*", "Updated to {}. ({})"): "{}へ更新しました。({})",
        ("*", "Failed to update {}. ({})"): "更新に失敗しました。{} ({})",

        # 3D Viewport > Sidebar > MMD > Model Production
        ("*", "Model Production"): "模型生产",
        ("Operator", "Create Model"): "创建新的模型",
        ("Operator", "Create a MMD Model Root Object"): "创建一个MMD模型的根物体",
        ("*", "Name(Eng)"): "名称(英文)",

        ("Operator", "Convert Model"): "转换模型",
        ("Operator", "Convert to a MMD Model"): "转换为MMD模型",
        ("*", "Ambient Color Source"): "环境色源",
        ("*", "Edge Threshold"): "边缘阈值",
        ("*", "Minimum Edge Alpha"): "最小边缘Alpha",
        ("*", "Convert Material Nodes"): "转换材质节点",
        ("*", "Middle Joint Bones Lock"): "中间关节骨锁定",

        ("Operator", "Attach Meshes"): "连接网格",

        ("Operator", "Translate"): "翻译",
        ("Operator", "Translate a MMD Model"): "翻译一个MMD模型",
        ("Operator", "(Experimental) Global Translation"): "(实验的) 全球翻译",
        ("*", "Dictionary"): "词典",
        ("*", "Modes"): "模式",
        ("*", "MMD Names"): "MMD名称",
        ("*", "Blender Names"): "Blender名称",
        ("*", "Use Morph Prefix"): "使用变形前缀",
        ("*", "Allow Fails"): "允许失败",

        ("*", "Model Surgery:"): "模型手术",
        ("Operator", "Chop"): "切断",
        ("Operator", "Peel"): "剥去",
        ("Operator", "Model Separate by Bones"): "用骨骼分离模型",
        ("*", "Separate Armature"): "分离骨架",
        ("*", "Include Descendant Bones"): "包括后代的骨骼",
        ("*", "Weight Threshold"): "权重阈值",
        ("*", "Boundary Joint Owner"): "边界的关节所有者",
        ("*", "Source Model"): "源模型",
        ("*", "Destination Model"): "目标模型",

        ("Operator", "Join"): "合并",
        ("Operator", "Model Join by Bones"): "用骨骼合并模型",
        ("*", "Join Type"): "接合类型",

        # 3D Viewport > Sidebar > MMD > Model Setup
        ("*", "Model Setup"): "模型设定",
        ("*", "Visibility:"): "可见性:",
        ("*", "Assembly:"): "装配:",
        ("Operator", "Physics"): "物理",
        ("Operator", "Build Rig"): "建立骨架",
        ("*", "Non-Collision Distance Scale"): "非碰撞距离缩放",
        ("*", "Collision Margin"): "碰撞边距",

        ("Operator", "SDEF"): "SDEF",
        ("Operator", "Bind SDEF Driver"): "绑定SDEF驱动器",
        ("*", "- Auto -"): "自动",
        ("*", "Bulk"): "散装",
        ("*", "Skip"): "略过",

        ("*", "IK Toggle:"): "IK切换:",

        ("*", "Mesh:"): "网格:",
        ("Operator", "Separate by Materials"): "按材质分开",
        ("Operator", "Join"): "合并",
        ("*", "Sort Shape Keys"): "排列形态键",

        ("*", "Material:"): "材质:",
        ("Operator", "Edge Preview"): "边缘预览",
        ("Operator", "Convert to Blender"): "转换给Blender",
        ("Operator", "Convert Materials"): "转换材质",
        ("*", "Convert to Principled BSDF"): "转换为原理化BSDF",
        ("*", "Clean Nodes"): "清理节点",

        ("*", "Misc:"): "杂项:",

        # 3D Viewport > Sidebar > MMD > Scene Setup
        ("*", "Scene Setup"): "场景设定",
        ("Operator", "MMD Tools/Manual"): "MMD Tools/使用手册",
        ("Operator", "Import"): "导入",
        ("Operator", "Export"): "导出",

        ("*", "Model:"): "模型:",
        ("*", "Types"): "类型",
        ("*", "Morphs"): "变形",
        ("*", "Clean Model"): "清空模型",
        ("*", "Fix IK Links"): "修复IK关联",
        ("*", "Apply Bone Fixed Axis"): "应用骨骼固定轴",
        ("*", "Rename Bones - L / R Suffix"): "将骨骼重命名 - L / R后缀",
        ("*", "Rename Bones - Use Underscore"): "将骨骼重命名 - 使用下划线",
        ("*", "Rename Bones To English"): "将骨骼重命名为英文",
        ("*", "Internal Dictionary"): "内部词典",
        ("*", "use MIP maps for UV textures"): "使用多级纹理进行UV纹理",
        ("*", "influence of .sph textures"): ".sph纹理的影响",
        ("*", "influence of .spa textures"): ".spa纹理的影响",
        ("*", "Log level"): "日志级别",
        ("*", "Create a log file"): "创建一个日志文件",
        ("*", "Copy textures"): "复制纹理",
        ("*", "Sort Materials"): "排列材质",
        ("*", "Disable SPH/SPA"): "禁用SPH/SPA",
        ("*", "Visible Meshes Only"): "只有可见的网格",
        ("*", "Overwrite Bone Morphs"): "覆盖骨骼变形",
        ("*", "Overwrite the bone morphs from active pose library before exporting."): "在导出前覆盖活动姿态库中的骨骼变形。",
        ("*", "(Experimental) Translate in Presets"): "(实验的) 预设中的翻译",
        ("*", "Translate in presets before exporting."): "导出前在预设中进行翻译。",
        ("*", "Sort Vertices"): "排列顶点",

        ("*", "Motion:"): "运动:",
        ("*", "Bone Mapper"): "骨骼映射器",
        ("*", "Renamed bones"): "重命名的骨骼",
        ("*", "Treat Current Pose as Rest Pose"): "把当前的姿态当作静置姿态",
        ("*", "Mirror Motion"): "镜像运动",
        ("*", "Update scene settings"): "更新场景设置",
        ("*", "Use Frame Range"): "使用帧范围",
        ("*", "Use NLA"): "使用NLA",

        ("*", "Pose:"): "姿态:",
        ("*", "Current Pose"): "当前的姿态",
        ("*", "Active Pose"): "活动的姿态",
        ("*", "All Poses"): "全部姿态",

        ("*", "Timeline:"): "时间线:",

        ("*", "Rigid Body Physics:"): "刚体物理:",
        ("Operator", "Update World"): "更新世界",
        ("*", "Substeps"): "子步数",
        ("*", "Iterations"): "迭代",

        # 3D Viewport > Sidebar > MMD > Display Panel
        ("*", "Display Panel"): "显示面板",
        ("Operator", "Bone"): "骨骼",
        ("Operator", "Morph"): "变形",
        ("Operator", "Add Display Item Frame"): "添加显示项目帧",
        ("Operator", "Remove Display Item Frame"): "移除显示项目帧",
        ("Operator", "Move Display Item Frame"): "移动显示项目帧",
        ("Operator", "Add Display Item"): "添加显示项目",
        ("Operator", "Remove Display Item"): "移除显示项目",
        ("Operator", "Move Display Item"): "移动显示项目",
        ("*", "Quick setup display items"): "快速设置显示项目",
        ("*", "Load Facial Items"): "载入面部项目",
        ("*", "Load Bone Groups"): "载入骨骼组",
        ("*", "Apply Bone Groups"): "应用骨骼组",
        ("Operator", "Move To Top"): "移至顶部",
        ("Operator", "Move To Bottom"): "移至底部",
        ("Operator", "Delete All"): "删除全部",

        # 3D Viewport > Sidebar > MMD > Morph Tools Panel
        ("*", "Morph Tools"): "变形工具",
        ("*", "Eye"): "眼",
        ("*", "Eye Brow"): "眼眉",
        ("*", "Mouth"): "嘴巴",
        ("Operator", "Add Morph"): "添加变形",
        ("Operator", "Remove Morph"): "移除变形",
        ("Operator", "Copy Morph"): "复制变形",
        ("Operator", "Overwrite Bone Morphs from active Pose Library"): "覆盖活动姿态库中的骨骼变形",
        ("Operator", "Move Morph"): "移动变形",
        ("Operator", "Add Morph Offset"): "添加变形偏移",
        ("Operator", "Remove Morph Offset"): "移除变形偏移",
        ("*", "Related Mesh"): "相关网格",
        ("Operator", "Create Work Material"): "创建工作材质",
        ("Operator", "Init Material Offset"): "初始化材质偏移",
        ("*", "Texture factor"): "纹理系数",
        ("*", "Sphere Texture factor"): "球体纹理系数",
        ("*", "Toon Texture factor"): "卡通纹理系数",

        # 3D Viewport > Sidebar > MMD > Rigid Bodies
        ("*", "Rigid Bodies"): "刚体",
        ("*", "Active Model"): "活动的模型",
        ("*", "All Models"): "全部模型",
        ("Operator", "Select Similar..."): "选择类似...",
        ("Operator", "Select Rigid Body"): "选择刚体",
        ("*", "Collision Group"): "碰撞组",
        ("*", "Collision Group Mask"): "碰撞组遮罩",
        ("*", "Rigid Type"): "刚类型",
        ("*", "Hide Others"): "隐藏其他",

        # 3D Viewport > Sidebar > MMD > Joints
        ("*", "Joints"): "关节",
        ("Operator", "Add Joint"): "添加关节",
        ("Operator", "Remove Joint"): "移除关节",

        # 3D Viewport > Sidebar > MMD > Material Sorter Panel
        ("*", "Material Sorter"): "材质顺序",
        ("*", "Select a mesh object"): "选择一个网格物体",
        ("*", "Use the arrows to sort"): "使用箭头来排序",
        ("Operator", "Move Material Up"): "移动材质",
        ("Operator", "Move Material Down"): "移动材质",

        # 3D Viewport > Sidebar > MMD > Meshes Sorter Panel
        ("*", "Meshes Sorter"): "网格顺序",
        ("*", "Select a MMD Model"): "选择一个MMD模型",
        ("Operator", "Move Object"): "移动物体",

        # 3D Viewport > Sidebar > MMD > Bone Order Panel
        ("*", "Bone Order"): "骨骼顺序",
        ("*", "After Dynamics"): "物理後",
        ("*", "Transform Order"): "変形階層",

        # 3D Viewport > Sidebar > Misc > MMD Display Panel
        ("*", "MMD Display"): "MMD显示",
        ("*", "Temporary Object"): "临时物体",
        ("*", "Rigid Body Name"): "刚体名称",
        ("*", "Joint"): "关节",
        ("*", "Joint Name"): "关节名称",
        ("*", "Toon Texture"): "卡通纹理",
        ("*", "Sphere Texture"): "球体纹理",
        ("*", "Property Drivers"): "属性驱动器",

        # 3D Viewport > Shading
        ("*", "MMD Shading Presets"): "MMD着色预设",
        ("Operator", "Shadeless"): "无明暗",

        # 3D Viewport > Menu > Object
        ("Operator", "Clean Shape Keys"): "清理形态键",

        # 3D Viewport > Menu > Pose
        ("Operator", "MMD Flip Pose"): "MMD翻转姿态",

        # 3D Viewport > Menu > Select
        ("Operator", "Select MMD Rigid Body"): "选择MMD刚体",

        # 3D Viewport > Sidebar > Misc > MMD Shading Panel
        ("*", "MMD Shading"): "MMD着色",
        ("Operator", "Shadeless"): "无明暗",

        # Properties > Object Properties > MMD Light Tools
        ("*", "MMD Light Tools"): "MMD灯光工具",
        ("Operator", "Convert to MMD Light"): "转换为MMD灯光",
        ("*", "Light Source"): "光源",

        # Properties > Object Properties > MMD Camera Tools
        ("*", "MMD Camera Tools"): "MMD摄像机工具",
        ("Operator", "Convert to MMD Camera"): "转换为MMD摄像机",
        ("*", "Camera Source"): "摄像机源",

        # Properties > Object Properties > MMD Model Information Panel
        ("*", "MMD Model Information"): "MMD模型信息",
        ("*", "Name (English)"): "名称(英文)",
        ("*", "Comment (English)"): "注释(英文)",
        ("Operator", "Change MMD IK Loop Factor"): "改变MMD IK循环系数",
        ("*", "MMD IK Loop Factor"): "MMD IK循环系数",
        ("Operator", "Recalculate bone roll"): "重算骨骼扭转",
        ("*", "This operation will break existing f-curve/action."): "这一操作将破坏现有的函数曲线/动作。",
        ("*", "Click [OK] to run the operation."): "点击[确定]来运行操作。",

        # Properties > Object Properties > MMD Rigid Body
        ("*", "MMD Rigid Body"): "MMD刚体",
        ("*", "Physics + Bone"): "物理 + 骨骼",
        ("*", "Collision Group Mask:"): "碰撞组遮罩:",

        # Properties > Object Properties > MMD Joint
        ("*", "MMD Joint"): "MMD关节",
        ("*", "X-Axis:"): "X轴:",
        ("*", "Y-Axis:"): "Y轴:",
        ("*", "Z-Axis:"): "Z轴:",
        ("*", "Spring(Linear)"): "弹簧(线性)",
        ("*", "Spring(Angular)"): "弹簧(棱角)",

        # Properties > Material Properties > MMD Material Panel
        ("*", "MMD Material"): "MMD材质",
        ("*", "Color:"): "颜色:",
        ("*", "Shadow:"): "阴影:",
        ("*", "Double Sided"): "双面",
        ("*", "Ground Shadow"): "地面阴影",
        ("*", "Self Shadow Map"): "自身阴影贴图",
        ("*", "Self Shadow"): "自身阴影",
        ("*", "Toon Edge"): "卡通边缘",
        ("*", "Edge Color"): "边缘颜色",
        ("*", "Edge Weight"): "边缘权重",

        # Properties > Material Properties > MMD Texture Panel
        ("*", "MMD Texture"): "MMD纹理",
        ("*", "Texture:"): "纹理:",
        ("*", "Sphere Texture:"): "球体纹理:",
        ("*", "SubTexture"): "次纹理",
        ("*", "Use Shared Toon Texture"): "使用共用的卡通纹理",
        ("*", "Shared Toon Texture"): "共用的卡通纹理",

        # Properties > Bone Properties > MMD Bone Tools Panel
        ("*", "MMD Bone Tools"): "MMD骨骼工具",
        ("*", "Information:"): "信息:",
        ("*", "Controllable"): "可控制的",
        ("*", "Tip Bone"): "尖端骨骼",
        ("*", "Fixed Axis"): "轴制限",
        ("*", "Local Axes"): "局部轴",
        ("*", "Local X-Axis"): "局部X轴",
        ("*", "Local Z-Axis"): "局部Z轴",
        ("*", "Rotate +"): "旋转 +",
        ("*", "Move +"): "移动 +",

        # Shader Editor > Shader Nodes
        ("*", "Base Tex Fac"): "基线纹理系数",
        ("*", "Base Tex"): "基线纹理",
        ("*", "Base Alpha"): "基线Alpha",
        ("*", "Base UV"): "基线UV",
        ("*", "Toon Tex Fac"): "卡通纹理系数",
        ("*", "Toon Tex"): "卡通纹理",
        ("*", "Toon Alpha"): "卡通Alpha",
        ("*", "Toon UV"): "卡通UV",
        ("*", "Sphere Tex Fac"): "球体纹理系数",
        ("*", "Sphere Tex"): "球体纹理",
        ("*", "Sphere Alpha"): "球体Alpha",
        ("*", "Sphere UV"): "球体UV",
        ("*", "Sphere Mul/Add"): "球体 乘法/加法",
        ("*", "SubTex UV"): "次纹理UV",

        # Operator Popup > Global Translation Popup
        ("Operator", "Global Translation Popup"): "全球翻译对话框",
        ("*", "is Blank:"): "是空白:",
        ("*", "Japanese"): "日文",
        ("*", "English"): "英文",
        ("*", "Select the target column for Batch Operations:"): "选择批量操作的目标列:",
        ("*", "Blender Name (name)"): "Blender名称 (name)",
        ("*", "Japanese MMD Name (name_j)"): "日文MMD名称 (name_j)",
        ("*", "English MMD Name (name_e)"): "英文MMD名称 (name_e)",
        ("*", "Batch Operation:"): "批量操作:",
        ("*", "Clear"): "清空",
        ("*", "Translate to English"): "翻译成英文",
        ("*", "Blender L/R to MMD L/R"): "将Blender的左右改为MMD的左右",
        ("*", "MMD L/R to Blender L/R"): "将MMD的左右改为Blender的左右",
        ("*", "Restore Blender Names"): "恢复Blender名称",
        ("*", "Restore Japanese MMD Names"): "名称日文MMD名称",
        ("*", "Restore English MMD Names"): "名称英文MMD名称",
        ("*", "Copy English MMD Names, if empty copy Japanese MMD Name"): "复制英文MMD名称，如果为空则复制日文MMD名称",
        ("*", "Copy Japanese MMD Names, if empty copy English MMD Name"): "复制日文MMD名称，如果为空则复制英文MMD名称",
        ("Operator", "Execute"): "执行",
        ("*", "Dictionaries:"): "词典:",
    },
}
