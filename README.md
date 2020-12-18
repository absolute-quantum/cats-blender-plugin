# Cats Blender Plugin (0.18.0)

A tool designed to shorten steps needed to import and optimize models into VRChat.
Compatible models are: MMD, XNALara, Mixamo, Source Engine, Unreal Engine, DAZ/Poser, Blender Rigify, Sims 2, Motion Builder, 3DS Max and potentially more

With Cats it takes only a few minutes to upload your model into VRChat.
All the hours long processes of fixing your models are compressed into a few functions!

So if you enjoy how this plugin saves you countless hours of work consider supporting us through Patreon.
There are a lot of perks like having your name inside the plugin!

[![](https://i.imgur.com/BFIald5.png)](https://www.patreon.com/catsblenderplugin)

#### Download here: [Cats Blender Plugin](https://github.com/michaeldegroot/cats-blender-plugin/archive/master.zip)

## Features
 - Optimizing model with one click!
 - Creating lip syncing
 - Creating eye tracking
 - Automatic decimation (while keeping shapekeys)
 - Creating custom models easily
 - Creating texture atlas
 - Creating root bones for Dynamic Bones
 - Optimizing materials
 - Translating shape keys, bones, materials and meshes
 - Merging bone groups to reduce overall bone count
 - Auto updater

*More to come!*

## Discord
Join our Discord to report errors, suggestions and make comments!

**Discord: https://discord.gg/f8yZGnv**

## Requirements
 - Blender **2.79** or **2.80** or above (run as administrator is recommended)
   - mmd_tools is **not required**! Cats comes pre-installed with it!
 - If you have custom Python installed which Blender might use, you need to have Numpy installed

## Installation
 - Download the plugin: **[Cats Blender Plugin](https://github.com/michaeldegroot/cats-blender-plugin/archive/master.zip)**
   - **Important: Do NOT extract the downloaded zip! You will need the zip file during installation!**
 - Install the addon in blender like so:
   - *This shows Blender 2.79. In Blender 2.80+ go to Edit > Preferences > Add-ons. Also you don't need to save the user settings there.*

![](https://i.imgur.com/eZV1zrs.gif)

 - Check your 3d view and there should be a new menu item called **CATS** ....w00t
   - Since Blender 2.80 the CATS tab is on the right in the menu that opens when pressing 'N'

![](https://i.imgur.com/pJfVsho.png)

 - If you need help figuring out how to use the tool (very outdated):

[![VRChat - Cat's Blender Plugin Overview](https://img.youtube.com/vi/0gu0kEj2xwA/0.jpg)](https://www.youtube.com/watch?v=0gu0kEj2xwA)

Skip the step where he installs "mmd_tools" in the video below, it's not needed anymore! (also very outdated)

[![VRChat - Importing an MMD to VRChat Megatutorial!](https://img.youtube.com/vi/7P0ljQ6hU0A/0.jpg)](https://www.youtube.com/watch?v=7P0ljQ6hU0A)

## Code contributors:
 - Hotox
 - Shotariya
 - Neitri
 - Kiraver
 - Jordo
 - Ruubick
 - feilen


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
  - Combining similar materials

##### Start Pose Mode
- Lets you test how bones will move.

##### Pose to Shape Key
- Saves your current pose as a new shape key.

##### Apply as Rest Pose
- Applies the current pose position as the new rest position. This saves the shape keys and repairs ones that were broken due to scaling


## Model Options

![](https://i.imgur.com/ZPj2VUJ.png)

##### Translation
- Translate certain entities from any japanese to english.
This uses an internal dictionary and Google Translate.

##### Separate by material / loose parts / shapes
- Separates a mesh by materials or loose parts or by whether or not the mesh is effected by a shape key

##### Join meshes
- Joins all/selected meshes together

##### Merge Weights
- Deletes the selected bones and adds their weight to their respective parents

##### Delete Zero Weight Bones
- Cleans up the bones hierarchy, deleting all bones that don't directly affect any vertices

##### Delete Constraints
- Removes constrains between bones causing specific bone movement as these are not used by VRChat

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

![](https://i.imgur.com/szIWglS.png)
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
  - Now you have two options:
    - Only move the mesh:
      - Uncheck the checkbox "Apply Transforms"
      - Move the mesh (and only the mesh!) of the merge armature to the desired position
        - You can use Move, Scale and Rotate
        - CATS will position the bones according to the mesh automatically
    - OR move the armature (and with it the mesh):
      - Check the checkbox "Apply Transforms"
      - Move the armature to the desired position
        - You can use Move, Scale and Rotate
        - Make sure that both meshes and armatures are at their correct positions as they will stay exactly like this
    - If you want to merge multiple objects from the same model it is often better to duplicate the armature for each of them and merge them individually
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

![](https://i.imgur.com/5u3teLp.png)

**Decimate your model automatically.**

##### Smart Decimation
- This will decimate all meshes while keeping every shapekey.

##### Save Decimation
- This will only decimate meshes with no shape keys.

##### Half Decimation
- This will only decimate meshes with less than 4 shape keys as those are often not used.

##### Full Decimation
- This will decimate your whole model deleting all shape keys in the process.

##### Custom Decimation
- This lets you choose the meshes and shape keys that should not be decimated.


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
  Split them across multiple atlases or reduce the individual texture sizes. This can be easily done in the MatCombiner tab.
- You can tell Unity to use up to 8k textures.
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


## Bake

![](https://user-images.githubusercontent.com/1109288/97830517-147d1500-1c82-11eb-8b20-feba732ad672.png)

**This is a non-destructive way to produce an optimized variant of (almost) any avatar!**

For more information please visit the **[Bake Panel Wiki Page](https://github.com/GiveMeAllYourCats/cats-blender-plugin/wiki/Bake)**.


## Shape Key

![](https://i.imgur.com/LgFK4KO.png)

**Apply Shape Key as Basis**
- Applies the selected shape key as the new Basis and creates a reverted shape key from the selected one.


## Settings and Updates

![](https://i.imgur.com/hYy7gD8.png)

**This plugin has an auto updater.**
It checks for a new version automatically once every day.

---

## Changelog

#### 0.18.0
- **Added Bake Panel!**
  - This is a non-destructive way to produce an optimized variant of (almost) any avatar!
  - Full credit goes to **feilen**! Thanks so much for this awesome feature <3
  - Check out the wiki for more information: https://github.com/GiveMeAllYourCats/cats-blender-plugin/wiki/Bake
- **Added Smart Decimation!**
  - This lets you decimate without loosing any shapekeys!
  - Full credit goes to **feilen**! Tons of thanks for this awesome feature as well <3
- **Added Japanese translation!**
  - Cats is now almost fully translated into Japanese
  - To use it simply change your Blender language to Japanese and then restart Blender
  - Full credit goes to **Jordo** and **Ruuubick**! Thank you so much <3
  - If you want to help translating Cats into any language, please us know!
- **General:**
  - Cats is now fully compatible with Blender 2.90 and 2.91
  - Added "Show mmd_tools tabs" option to Settings
    - This allows you show and hide the "MMD" and "Misc" tabs added by the mmd_tools plugin
  - Added button to "Start/Stop Pose Mode" which starts/stops pose mode without resetting the current pose
  - Changed link to a new vrm importer since the old one dropped support
  - Fixed Google Translations no longer working
  - Fixed bug in "Apply as Rest Pose" and "Pose to Shape Key" in Blender 2.90
  - More fixes for Blender 2.90
  - NOTE: Using Cats in Blender 2.90+ on Ubuntu might cause Blender to crash on load (caused by mmd_tools)
    - To fix this use a Blender version prior to 2.90 or try updating your drivers

#### 0.17.0
- **Cats is now fully compatible with Blender 2.83!**
  - *It was compatible with 2.82 all long*
- **Fix Model:**
  - Added "Keep Twist Bones" option to Fix Model
    - This will keep any bone containing 'Twist'
  - Added "Fix MMD Twist Bones" option to Fix Model
    - This will apply a fix to make the MMD arm twist bones usable **(Thanks Rokk!)**
    - You do not need to enable "Keep Twist Bones" for this to work
  - Added "Remove Rigidbodies and Joints" option to Fix Model
    - This is solely intended for our non-VRChat users
  - Added compatibility to more models
  - Disabling the option "Remove Zero Weight Bones" now also keeps unused vertex groups
- **Importer:**
  - Imported meshes from VRM files now get automatically parented to their armature
  - Imported armatures now always show their bones in front and in wire mode
  - Fixed export warning being empty
  - Fixed importer error when the FBX importer was not enabled
  - Fixed importer error when a zip file contained another zip file
  - When importing a model, objects of a new scene now only get deleted if all three of them are present
- **Custom Model Creation:**
  - Added "Remove Zero Weight Bones" option to Merge Armatures
- **Decimation:**
  - Added "Remove Doubles" option
- **General:**
  - Fixed some bugs
  - Fixed objects getting unhidden when doing any cats operation in 2.80+
  - Updated mmd_tools

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
