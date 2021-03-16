using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor;
using UnityEditor.PackageManager;
using System;

[ExecuteInEditMode]
public class BakeFixer : MonoBehaviour
{
    [InitializeOnLoadMethod]
    private static void InitializeOnLoad()
    {
    	Scene scene = SceneManager.GetActiveScene();
    	var game_obj = scene.GetRootGameObjects();
    	foreach (var obj in game_obj)
    	{
    		// For each armature on the scene who owns "Armature", "Static" and "Body",
    		// get their SkinnedMeshRenderer components and edit the anchor point
            // TODO: Also ensure they share the same folder as this script!
    		if (obj.transform.Find("Armature") != null &&
    		    obj.transform.Find("Body") != null &&
    		    obj.transform.Find("Static") != null)
    		{
    			var body = obj.transform.Find("Body");
    			var stat = obj.transform.Find("Static");
    			var arm = obj.transform.Find("Armature");
                if (arm.childCount > 0 && arm.Find("Hips") != null)
                {
    			    Debug.Log("Altering anchor point for: " + obj.name);
                    var hips = arm.Find("Hips");
    			    var smr_body = (SkinnedMeshRenderer)body.GetComponent(typeof(SkinnedMeshRenderer));
    			    var smr_stat = (SkinnedMeshRenderer)body.GetComponent(typeof(SkinnedMeshRenderer));
                
                    // Set lightprobe anchor
                    smr_body.probeAnchor = hips;
                    smr_stat.probeAnchor = hips;
                } else {
                    Debug.Log("Couldn't find Hips for: " + obj.name);
                }
	    	}	
    	}
   }
}
