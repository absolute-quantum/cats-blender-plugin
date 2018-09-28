# Cats Blender Plugin (0.11.1)

A tool designed to shorten steps needed to import and optimize models into VRChat.
Compatible models are: MMD, XNALara, Mixamo, Source Engine, Unreal Engine, DAZ/Poser, Blender Rigify, Sims 2, Motion Builder, 3DS Max and potentially more

With Cats it takes only a few minutes to upload your model into VRChat.
All the hours long processes of fixing your models are compressed into a few functions!

So if you enjoy how this plugin saves you countless hours of work consider supporting us through Patreon:

[![](https://i.imgur.com/BFIald5.png)](https://www.patreon.com/catsblenderplugin)

Master branch: ![](https://api.travis-ci.org/michaeldegroot/cats-blender-plugin.svg?branch=master)

Development branch: ![](https://api.travis-ci.org/michaeldegroot/cats-blender-plugin.svg?branch=development)

## Features
 - Optimizing model with one click!
 - Creating lip syncing
 - Creating eye tracking
 - Automatic decimation
 - Creating custom models easily
 - Creating texture atlas
 - Creating root bones for Dynamic Bones
 - Optimizing materials
 - Translating shape keys, bones, materials and meshes
 - Merging bone groups to reduce overall bone count
 - Protecting your avatars from game cache ripping
 - Auto updater

*More to come!*

## Website
Check our website to report errors, suggestions or make comments!
https://catsblenderplugin.com

## Requirement

 - Blender 2.79 **(run as administrator)**
   - mmd_tools is **no longer required**! Cats comes pre-installed with it!

## Installation
 - Download the plugin: [Cats Blender Plugin](https://github.com/michaeldegroot/cats-blender-plugin/archive/master.zip)
 - Install the the addon in blender like so:

![](https://i.imgur.com/eZV1zrs.gif)

 - Check your 3d view and there should be a new menu item called **CATS** ....w00t

![](https://i.imgur.com/ItJLtNJ.png)

 - If you need help figuring out how to use the tool:

[![VRChat - Cat's Blender Plugin Overview](https://img.youtube.com/vi/0gu0kEj2xwA/0.jpg)](https://www.youtube.com/watch?v=0gu0kEj2xwA)

Skip the step where he installs "mmd_tools" in the video below, it's not needed anymore!

[![VRChat - Importing an MMD to VRChat Megatutorial!](https://img.youtube.com/vi/7P0ljQ6hU0A/0.jpg)](https://www.youtube.com/watch?v=7P0ljQ6hU0A)

## Code contributors:
 - Hotox
 - Shotariya
 - Neitri
 - Kiraver


## Model
![](https://i.imgur.com/dYYAfb4.png)

This tries to completely fix your model with one click.

##### Import/Export Model
- Imports a model of the selected type with the optimal settings
- Exports a model as an .fbx with the optimal settings

##### Fix Model
- Fixes your model automatically by:
  - Reparenting bones
  - Removing unnecessary bones
  - Renaming and translating objects and bones
  - Mixing weight paints
  - Rotating the hips
  - Joining meshes
  - Removing rigidbodies, joints and bone groups
  - Removing bone constraints
  - Deleting unused vertex groups
  - Using the correct shading
  - Making it compatible with Full Body Tracking
 
 **special thanks to @ProfessorSnep#0001, @Mimi#4114, @persia#0123 and @Gallium#7020 <3 <3**

##### Start Pose Mode
- Lets you test how bones will move.

##### Pose to Shape Key
- Saves your current pose as a new shape key.

##### Apply as Rest Pose
- Applies the current pose position as the new rest position. This saves the shape keys and repairs ones that were broken due to scaling


## Model Options

![](https://i.imgur.com/jlxQCvH.png)

##### Translation
- Translate certain entities from any japanese to english.
This uses an internal dictionary and Google Translate.

##### Separate by material / loose parts
- Separates a mesh by materials or loose parts

##### Join meshes
- Joins all meshes together

##### Delete Zero Weight Bones
- Cleans up the bones hierarchy, deleting all bones that don't directly affect any vertices

##### Delete Constraints
- Removes constrains between bones causing specific bone movement as these are not used by VRChat

##### Merge Weights
- Deletes the selected bones and adds their weight to their respective parents

##### Recalculate Normals
- Makes normals point inside of the selected mesh
- Don't use this on good looking meshes as this can screw them up

##### Flip Normals
- Flips the direction of the faces' normals of the selected mesh.

##### Apply Transformations
- Applies the position, rotation and scale to the armature and its meshes.

##### Remove Doubles
- Merges duplicated faces and vertices of the selected meshes.


## Custom Model Creation

![](https://i.imgur.com/epkhkmy.png)
![](https://i.imgur.com/04O63q1.png)

**This makes creating custom avatars a breeze!**

##### Merge Armatures
- Merges the selected armature into the selected base armature.
- **How to use:**
  - Use "Fix Model" on both armatures
    - Select the armature you want to fix in the list above the Fix Model button
    - Ignore the "Bones are missing" warning if one of the armatures is incomplete (e.g hair only)
    - If you don't want to use "Fix Model" make sure that the armature follows the CATS bone structure (https://i.imgur.com/F5KEt0M.png)
    - DO NOT delete any main bones by yourself! CATS will merge them and delete all unused bones afterwards
  - Move the mesh (and only the mesh!) of the merge armature to the desired position
    - You can use Move, Scale and Rotate
    - CATS will position the bones according to the mesh automatically
    - If you want multiple objects from the same model it is often better to duplicate the armature for each of them and merge them individually
  - Select the base armature and the armature you want to merge into the base armature in the panel
  - If CATS can't detect the bone structure automatically: select a bone you want to attach the new armature to
    - E.g.: For a hair armature select "Head" as the bone
  - Press the "Merge Armatures" button -> Done!

##### Attach Mesh to Armature
- Attaches the selected mesh to the selected armature.
- **How to use:**
  - Move the mesh to the desired position
    - You can use Move, Scale and Rotate
    - INFO: The mesh will only be assigned to the selected bone
    - E.g.: A jacket won't work, because it requires multiple bones.
    - E.g.: A ring on a finger works perfectly, because the ring only needs one bone to move with (the finger bone)
  - Select the base armature and the mesh you want to attach to the base armature in the panel
  - Select the bone you want to attach the mesh to in the panel
  - Press the "Attach Mesh" button -> Done!

##### Support us:
- We worked hard on this feature. If you like it consider supporting us, it helps a lot!

[![](https://i.imgur.com/BFIald5.png)](https://www.patreon.com/catsblenderplugin)


## Decimation

![](https://i.imgur.com/vozxKy9.png)

**Decimate your model automatically.**

##### Save Decimation
- This will only decimate meshes with no shape keys.

##### Half Decimation
- This will only decimate meshes with less than 4 shape keys as those are often not used.

##### Full Decimation
- This will decimate your whole model deleting all shape keys in the process.

##### Custom Decimation
- This will let you choose which meshes and shape keys should not be decimated.


## Eye Tracking
![](https://i.imgur.com/yw8INDO.png)
![](https://i.imgur.com/VHw73zM.png)

**Eye tracking is used to artificially track someone when they come close to you.**
It's a good idea to check the eye movement in the testing tab after this operation to check the validity of the automatic eye tracking creation.

##### Disable Eye Blinking
- Disables eye blinking. Useful if you only want eye movement.

##### Disable Eye Movement
- Disables eye movement. Useful if you only want blinking. **IMPORTANT:** Do your decimation first if you check this!

##### Eye Movement Speed
- Configure eye movement speed


## Visemes (Lip Sync)
![](https://i.imgur.com/muM2PTS.png)

**Mouth visemes are used to show more realistic mouth movement in-game when talking over the microphone.**
The script generates 15 shape keys from the 3 shape keys you specified. It uses the mouth visemes A, OH and CH to generate this output.


## Bone parenting

![](https://i.imgur.com/mgadT4R.png)

**Useful for Dynamic Bones where it is ideal to have one root bone full of child bones.**
This works by checking all bones and trying to figure out if they can be grouped together, which will appear in a list for you to choose from. After satisfied with the selection of this group you can then press 'Parent bones' and the child bones will be parented to a new bone named RootBone_xyz

##### To parent
- List of bones that look like they could be parented together to a root bone. Select a group of bones from the list and press "Parent bones"

##### Refresh list
- Clears the group bones list cache and rebuild it, useful if bones have changed or your model

##### Parent bones
- Starts the parent process


## Texture atlas
![](https://i.imgur.com/XcoF0Ek.png)

**Texture atlas is the process of combining multiple textures into one to drastically reduce draw calls and therefore make your model much more performant**

##### Create Atlas
- Combines all selected materials into one texture. If no material list is generated it will combine all materials.

##### Generate Material List
- Lists all materials of the current model and lets you select which ones you want to combine.

### Useful Tips:
- Split transparent and non-transparent textures into separate atlases to avoid transparency issues
- Make sure that the created textures are not too big, because Unity will downscale them to 2048x2048. 
  Split them across multiple atlases or reduce the texture size manually beforehand
- You can also tell Unity to use up to 8k textures.
  Do so by selecting the texture and then choose a different Max Size and/or Compression in the inspector:
  https://i.imgur.com/o01T4Gb.png


## Bone merging

![](https://i.imgur.com/FXwOvho.png)

**Lets you reduce overall bone count in a group set of bones.**
This works by checking all bones and trying to figure out if they can be grouped together, which will appear in a list for you to choose from. After satisfied with the selection of this group you can then set a percentage value how much bones you would like to merge together in itself and press 'Merge bones'

##### Refresh list
- Clears the group bones list cache and rebuild it, useful if bones have changed or your model

##### Merge bones
- Starts the merge process


## Copy Protection

![](https://i.imgur.com/5qP5bCT.png)

**Can protect your avatars from being ripped from the game cache.**
Game cache rips in most common cases do not include blendshapes and shaders. 
This method will make it much harder for people that try to steal your avatar through ripping from cache.

**We managed to fix the lighting bugs! Therefore the randomization options are not needed anymore.**


#### How to setup:

1. Do all the modifications to your model in Blender before you follow the next steps!
   This option should be the last one you do in Blender before exporting!
2. You won't be able to see the mesh of your model inside the Unity bone mapping screen (it will be garbled mess, but only in there).
   Because of that, if you need to actually see your models mesh (e.g. for straightening the fingers for VR), follow the extra steps below.
   If you don't need to see the mesh (e.g. for unassigning the jaw bone) skip to step 2.
     - Export your model from Blender without enabling the protection
     - Load it up in Unity and configure it in the bone mapping screen and press "Done"
     - In Blender: Click the "Enable Protection" button and export your model
     - Then, except for just dragging the fbx into Unity, you need to go into the folder where this Unity project is located
       and then replace the unprotected fbx with the protected one. 
       That way your configurations will be kept.
     - Skip to step 5
3. In Blender: Click the "Enable Protection" button
4. Export it to Unity by either using the "Export" button within Cats or set the fbx export option by yourself: 
   Geometries > Smoothing > Set to "Face"
5. In Unity: Set the value of the blendshape 'Basis Original' to 100 like so: 
   https://i.imgur.com/RlrGTvV.gif
6. To fix any lighting issues select your .fbx and then select "Import" as the Tangents option here: 

   ![](https://i.imgur.com/SqynQzw.png)
7. Because (for some odd reason) the protection increases your bounding box it could be too big to upload your model.
   If the VRCSDK complains about your model being too large, edit your bounding box back to normal here:
   (this option is below the blendshape list from above)
   
   ![](https://i.imgur.com/4NrfVOr.png)
8. Your avatar now behaves just like a normal one.

People that try to steal your avatar will then only see a box of mangled waifu trash instead of your original character.

  **special thanks to @zarniwoop#6081**


## Shape Key

![](https://i.imgur.com/LgFK4KO.png)

**Apply Shape Key as Basis**
- Applies the selected shape key as the new Basis and creates a reverted shape key from the selected one.


## Update Plugin

![](https://i.imgur.com/ltcTRlR.png)

**This plugin has an auto updater.**
It checks for a new version automatically once every day.


## Changelog

#### 0.11.1
- **Translations:**
  - Added a warning when you are temporarily IP banned by Google Translate

#### 0.11.0
- **Optimization:**
  - Added new greatly improved Auto Atlas method made by **shotariya**!
    - This new method will create near perfect texture atlases automatically
    - You will need to install the (extremely awesome) plugin "Material Combiner" made by shotariya
    - If you don't have it installed, CATS will provide you with a download link
    - CATS packs the functions into a single-click button
    - If you want more options, use the plugin tab "shotariya"
- **Export:**
  - Added warning when meshes have more than 65354 tris or more than 10 materials/meshes
  - Improved CATS FBX Export settings (Thanks Rokk!)
    - Textures will now be stored inside the FBX file
    - When importing the FBX file into Unity, the textures will be imported automatically as well
    - The scale of armatures and meshes in Unity will now always be 1 instead of being set to 100 sometimes
    - This fixes possible bugs with mesh particles
    - If you want to overwrite old FBX files with the new ones in Unity, you might have to enforce the T-Pose again. Newly imported FBX files are uneffected by this
- **Model:**
  - A lot more models are now compatible
  - Added fix for bad uv coordinates (Thanks shotariya!)
  - Join Meshes now adds missing armature modifiers
    - This prevents cases where the mesh would not move with the bones
  - Join Meshes now merges UV Maps correctly
    - This fixes disappearing textures which were previously there
  - Fix Model now unlocks all transformations on armature, mesh and bones
  - Added warning if the FBX version is too old
  - Using "Pose to Shape Key" or "Apply as Rest Pose" no longer requires you to join the meshes
  - "Apply as Rest Pose" now correctly scales shape keys if the bones are equally scaled on each axis
  - Fixed "Apply as Rest Pose" sometimes selecting the wrong shape key after the operation
  - Finally fixed CATS deleting bones and then claiming that they are missing
- **Custom Model:**
  - Added option to merge all bones that have the same name
  - Merge Armatures and Attach Mesh now remove all empty shapekeys afterwards
- **Eye Tracking:**
  - Eye bones should no longer be created in weird places
  - Fixed a bug where old vertex groups were not getting deleted
- **General:**
  - Lots of bug fixes
  - Updated mmd_tools
  - Added future proof Google Translate maintenance fix (Thanks BlueLament!)

#### 0.10.1
- **Model:**
  - Fixed "Apply as Rest Pose" deleting important shape keys
- **Translations:**
  - Added option to use the old translations for shapekey translations
- **Optimization:**
  - Fixed rare error when combining materials

Read the full changelog [here](https://github.com/michaeldegroot/cats-blender-plugin/releases).


## Roadmap
 - MOAR updates on the armature code
 - Texture translation should have an option to rename the filename also
 - Automatic lower lid creation for eye tracking
 - Manual bone selection button for root bones
 - Full body tracking proportion adjustments


## Feedback
Do you love this plugin or have you found a bug?
Post a response in this thread or send your feedback to the official discord server of the plugin for real-time communication: https://discord.gg/f8yZGnv and look for people with the developer role ;)


## Support us
If you enjoy how this plugin saves you countless hours of work consider supporting us through Patreon:

[![](https://i.imgur.com/BFIald5.png)](https://www.patreon.com/catsblenderplugin)
