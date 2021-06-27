#if UNITY_EDITOR
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor;
using System;
using System.IO;

[InitializeOnLoad]
public class BakeFixer : ScriptableObject
{
    static BakeFixer()
    {
        EditorApplication.hierarchyChanged += Update;
        Debug.Log("BakeFixer loaded");
    }

    static void Update()
    {
        // Get the path of this script
        Scene scene = SceneManager.GetActiveScene();
        var game_obj = scene.GetRootGameObjects();
        foreach (var obj in game_obj)
        {
            // For each armature on the scene who owns "Armature", "Static" and "Body",
            // get their SkinnedMeshRenderer components and edit the anchor point
            if (obj.transform.Find("Armature") != null &&
                    obj.transform.Find("Body") != null &&
                    obj.transform.Find("Static") != null)
            {
                var body = obj.transform.Find("Body");
                var stat = obj.transform.Find("Static");
                var arm = obj.transform.Find("Armature");
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
#endif
