# Cats Blender Plugin (0.6.1)

A tool designed to shorten steps needed to import and optimize models into VRChat.
Compatible models are: MMD, XNALara, Mixamo, DAZ/Poser, Blender Rigify, Sims 2, Motion Builder, 3DS Max and potentially more

Development branch: ![](https://api.travis-ci.org/michaeldegroot/cats-blender-plugin.svg?branch=development)

Master branch: ![](https://api.travis-ci.org/michaeldegroot/cats-blender-plugin.svg?branch=master)

[![](https://i.imgur.com/BFIald5.png)](https://www.patreon.com/catsblenderplugin)

## Website
Check our website to report errors, suggestions or make comments!
https://catsblenderplugin.com

## Features
 - Optimizing model with one click!
 - Creating lip syncing
 - Creating eye tracking
 - Automatic decimation
 - Creating texture atlas
 - Creating root bones for Dynamic Bones
 - Optimizing materials
 - Translating shape keys, bones, materials and meshes
 - Merging bone groups to reduce overall bone count
 - Auto updater

*More to come!*

## Requirements

 - Blender 2.79 (run as administrator)
 - [powroupi/mmd tools](https://github.com/powroupi/blender_mmd_tools) (dev_test branch)

## Installation
 - Install this Blender plugin if you don't have it already: [mmd_tools](https://github.com/powroupi/blender_mmd_tools/archive/dev_test.zip)
 - Download the plugin: [Cats Blender Plugin](https://github.com/michaeldegroot/cats-blender-plugin/archive/master.zip)
 - Install the the addon in blender like so:

![](https://i.imgur.com/eZV1zrs.gif)

 - Check your 3d view and there should be a new menu item called **CATS** ....w00t

![](https://i.imgur.com/ItJLtNJ.png)

 - If you need help figuring out how to use the tool:

[![VRChat - Cat's Blender Plugin Overview](https://img.youtube.com/vi/0gu0kEj2xwA/0.jpg)](https://www.youtube.com/watch?v=0gu0kEj2xwA)

[![VRChat - Importing an MMD to VRChat Megatutorial!](https://img.youtube.com/vi/7P0ljQ6hU0A/0.jpg)](https://www.youtube.com/watch?v=7P0ljQ6hU0A)


## Code contributors:
 - Hotox
 - Shotariya
 - Neitri
 - Kiraver


## Model
![](https://i.imgur.com/gw66CMj.png)

This tries to completely fix your model with one click.

##### Fix model
Fixes your model automatically by:
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

##### Delete zero weight bones
Cleans up the bones hierarchy, because MMD models usually come with a lot of extra bones that don't directly affect any vertices.

##### Import model
Imports a model.

##### Separate by material
Separatres a mesh by materials

##### Join meshes
Joins all meshes into one

##### Mix weights
Deletes the selected bones and adds their weight to their respective parents.


## Translation

![](https://i.imgur.com/SCyhVn1.png)

**Can translate certain entities from any language to english** Works by sending a request to the Google translate service. This feature can be slow for entities with a large amount of items.


## Decimation

![](https://i.imgur.com/DOjZR8G.png)

**Decimate your model automatically**

##### Save Decimation
This will only decimate meshes with no shape keys.

##### Half Decimation
This will only decimate meshes with less than 4 shape keys as those are often not used.

##### Full Decimation
This will decimate your whole model deleting all shape keys in the process.


## Eye tracking
![](https://i.imgur.com/yw8INDO.png)
![](https://i.imgur.com/VHw73zM.png)

**Eye tracking is used to artificially track someone when they come close to you**
It's a good idea to check the eye movement in pose mode after this operation to check the validity of the automatic eye tracking creation.

### Properties

##### Mesh
The mesh with the eyes vertex groups

##### Head
Head bone name

##### Left eye
Eye bone left name

##### Right eye
Eye bone right name

##### Blink left
The name of the shape key that controls wink left

##### Blink right
The name of the shape key that controls wink right

##### Lowerlid left
The name of the shape key that controls lowerlid left

##### Lowerlid right
The name of the shape key that controls lowerlid right

##### Disable Eye Blinking
Disables eye blinking. Useful if you only want eye movement.

##### Disable Eye Movement
Disables eye movement. Useful if you only want blinking. **IMPORTANT:** Do your decimation first if you check this!

##### Eye Movement Speed
Configure eye movement speed


## Mouth visemes
![](https://i.imgur.com/z6imAYn.png)

**Mouth visemes are used to show more realistic mouth movement in-game when talking over the microphone**
The script generates 15 shape keys from the 3 shape keys you specified. It uses the mouth visemes A, OH and CH to generate this output.
*This is still an experimental feature and will be fine tuned over the course of time*

### Properties

##### Mesh
The mesh with the mouth shape keys

##### Viseme AA
Shape key containing mouth movement that looks like someone is saying "aa"

##### Viseme OH
Shape key containing mouth movement that looks like someone is saying "oh"

##### Viseme CH
Shape key containing mouth movement that looks like someone is saying "ch". Opened lips and clenched teeth

##### Shape key mix intensity
Controls the strength in the creation of the shape keys. Lower for less mouth movement strength.


## Bone parenting

![](https://i.imgur.com/mgadT4R.png)

**Useful for Dynamic Bones where it is ideal to have one root bone full of child bones**
This works by checking all bones and trying to figure out if they can be grouped together, which will appear in a list for you to choose from. After satisfied with the selection of this group you can then press 'Parent bones' and the child bones will be parented to a new bone named RootBone_xyz

##### To parent
This is a list of bones that look like they could be parented together to a root bone. Select a group of bones from the list and press "Parent bones"

##### Refresh list
This will clear the group bones list cache and rebuild it, useful if bones have changed or your model

##### Parent bones
This will start the parent process


## Texture atlas
![](https://i.imgur.com/qiD9jAA.png)

**Texture atlas is the process of combining multiple textures into one to save processing power to render one's model**
If you are unsure about what to do with the margin and angle setting, then leave it default. The most important setting here is texture size and target mesh.

### Properties

##### Margin
Margin to reduce bleed of adjacent islands

##### Angle
Lower for more projection groups, higher for less distortion

##### Texture size
Lower for faster bake time, higher for more detail.

##### Area Weight
Weight projections vector by faces with larger areas

##### Target mesh
The mesh that you want to create an atlas from

##### One Texture Material
Texture baking and multiple textures per material can look weird in the end result. Check this box if you are experiencing this.
**If any experienced blender user can tell me how to fix this more elegantly please do let me know!**


## Bone merging

![](https://i.imgur.com/S88JLJd.png)

**Lets you reduce overall bone count in a group set of bones**
This works by checking all bones and trying to figure out if they can be grouped together, which will appear in a list for you to choose from. After satisfied with the selection of this group you can then set a percentage value how much bones you would like to merge together in itself and press 'Merge bones'

##### To merge
This is a list of bones that look like they could be merged together. Select a group of bones from the list and press "Merge bones"

##### Refresh list
This will clear the group bones list cache and rebuild it, useful if bones have changed or your model

##### Merge bones
This will start the merge process


## Update Plugin
There is an auto updater in the plugin so you don't have to keep checking for new version. This is how to check for updates:

![](https://i.imgur.com/LbO7Xst.gif)


## Changelog

#### 0.6.2
- Added: Model: More models are now compatible (please report non working models to us)
- Fixed: Bone Merging: No longer deletes random bones sometimes

#### 0.6.1
- Added: Model: A lot more models are now compatible (please report non working models to us)
- Added: Model: Added "Pose to Shape Key" button when in pose mode. This converts the current pose into a shape key
- Changed: Eye Tracking: Improved error messages
- Fixed: Eye Tracking: Fixed a bug where the mouth would stay open after creating eye tracking
- Fixed: Decimation: Fixed a bug where decimation would failed due to division by zero
- Fixed: Model: Fixed a bug where root bones created by cats got deleted
- Fixed: Materials: Fixed an error when the texture files don't exist
- Fixed: Translation: Shape keys created by cats no longer get translated
- Fixed: Small spelling mistake
- Fixed: More bugs

#### 0.6.0
- Added: Model: Added support for DAZ/Poser, Blender Rigify, Sims 2, Motion Builder and 3DS Max models
- Added: Model: Added support for models with more than 2 spines
- Added: Model: Added conversion of mmd bone morphs into shape keys
- Added: Model: Added import option for XNALara and FBX
- Added: Model: Now resets the pivot to the center
- Added: Model: Added Export button
- Added: Model: Importing and Exporting now automatically sets the optimal settings
- Added: Decimation: Added custom decimation tab, allows you to whitelist meshes and shape keys
- Added: Decimation: Added option to exclude fingers from decimation
- Added: General: Warning when Blender is outdated
- Fixed: Atlas: Fixed transparency issue after creating auto atlas
- Fixed: Material: Fixed an issue where materials were wrongly merged together (Thanks kiraver!)
- Fixed: Model: Multiple parenting issues
- Fixed: Bugs from every corner

See the full changelog [here](https://github.com/michaeldegroot/cats-blender-plugin/releases).


## Roadmap
 - Full body tracking support
 - MOAR updates on the armature code
 - Texture translation should have an option to rename the filename also
 - Automatic lower lid creation for eye tracking
 - Manual bone selection button for root bones


## Feedback
Do you love this plugin or have you found a bug?
Post a response in this thread or send your feedback to the official discord server of the plugin for real-time communication: https://discord.gg/f8yZGnv and look for people with the developer role ;)
