#if !BAKEFIXER_{IFDEFNAME}
#define BAKEFIXER_{IFDEFNAME}
#if UNITY_EDITOR
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor;
using System;
using System.IO;

[InitializeOnLoad]
public class BakeFixer_{BODYNAME} : ScriptableObject
{
    static BakeFixer_{BODYNAME}()
    {
        EditorApplication.hierarchyChanged += Update;
        Debug.Log("BakeFixer loaded for {BODYNAME}");
    }

    static void Update()
    {
        // Get the path of this script
        Scene scene = SceneManager.GetActiveScene();
        var game_obj = scene.GetRootGameObjects();
        foreach (var obj in game_obj)
        {
            // For each armature on the scene who owns "{ARMATURENAME}", "Static" and "{BODYNAME}",
            // get their SkinnedMeshRenderer components and edit the anchor point
            if (obj.transform.Find("{ARMATURENAME}") != null &&
                    obj.transform.Find("{BODYNAME}") != null &&
                    obj.transform.Find("Static") != null)
            {
                var body = obj.transform.Find("{BODYNAME}");
                var stat = obj.transform.Find("Static");
                var arm = obj.transform.Find("{ARMATURENAME}");
                var smr_body = (SkinnedMeshRenderer)body.GetComponent(typeof(SkinnedMeshRenderer));
                var smr_stat = (SkinnedMeshRenderer)stat.GetComponent(typeof(SkinnedMeshRenderer));

                if (arm.childCount > 0) {
                    Debug.Log("Altering anchor point for: " + obj.name);
                    var hips = arm.GetChild(0);

                    // Set lightprobe anchor
                    smr_body.probeAnchor = hips;
                    smr_stat.probeAnchor = hips;
                }
            }
        }
    }
}
#endif // UNITY_EDITOR
#endif // BAKEFIXER_{BODYNAME}
