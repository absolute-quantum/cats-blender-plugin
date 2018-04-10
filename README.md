# Cats Blender Plugin (0.7.0)

A tool designed to shorten steps needed to import and optimize models into VRChat.
Compatible models are: MMD, XNALara, Mixamo, Unreal Engine, DAZ/Poser, Blender Rigify, Sims 2, Motion Builder, 3DS Max and potentially more

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
 - Creating texture atlas
 - Creating root bones for Dynamic Bones
 - Optimizing materials
 - Translating shape keys, bones, materials and meshes
 - Merging bone groups to reduce overall bone count
 - Auto updater

*More to come!*

## Website
Check our website to report errors, suggestions or make comments!
https://catsblenderplugin.com

## Requirement

 - Blender 2.79 (run as administrator)
   - mmd_tools is **no longer required**! Cats comes pre-installed with it!

## Installation
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
![](https://i.imgur.com/d1yhtHp.png)

This tries to completely fix your model with one click.

##### Import model
Imports a model with the selected type.

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

##### Separate by material / loose parts
Separates a mesh by materials or loose parts

##### Join meshes
Joins all meshes into one

##### Mix weights
Deletes the selected bones and adds their weight to their respective parents.

##### Start Pose Mode
Lets you test how bones will move.

##### Pose to Shape Key
Saves your current pose as a new shape key.


## Translation

![](https://i.imgur.com/SCyhVn1.png)

**Can translate certain entities from any language to english** Works by sending a request to the Google translate service. This feature can be slow for entities with a large amount of items.


## Decimation

![](https://i.imgur.com/vozxKy9.png)

**Decimate your model automatically**

##### Save Decimation
This will only decimate meshes with no shape keys.

##### Half Decimation
This will only decimate meshes with less than 4 shape keys as those are often not used.

##### Full Decimation
This will decimate your whole model deleting all shape keys in the process.

##### Custom Decimation
This will let you choose which meshes and shape keys should not be decimated.


## Eye tracking
![](https://i.imgur.com/yw8INDO.png)
![](https://i.imgur.com/VHw73zM.png)

**Eye tracking is used to artificially track someone when they come close to you**
It's a good idea to check the eye movement in pose mode after this operation to check the validity of the automatic eye tracking creation.

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

![](https://i.imgur.com/FXwOvho.png)

**Lets you reduce overall bone count in a group set of bones**
This works by checking all bones and trying to figure out if they can be grouped together, which will appear in a list for you to choose from. After satisfied with the selection of this group you can then set a percentage value how much bones you would like to merge together in itself and press 'Merge bones'

##### Refresh list
This will clear the group bones list cache and rebuild it, useful if bones have changed or your model

##### Merge bones
This will start the merge process


## Update Plugin
There is an auto updater in the plugin so you don't have to keep checking for a new version.

![](https://i.imgur.com/ltcTRlR.png)


## Changelog

#### 0.7.0
- Added: mmd_tools is no longer required! Cats now automatically comes with it!
  - You should uninstall all previous versions of mmd_tools for the best result!
  - If you want to use your own mmd_tools load it after Cats!
- Added: Model: Unreal Engine models are now supported!
- Added: Model: More models are now compatible (please report non working models to us)
- Added: Model: New "Separate by Loose Parts" button
- Added: Model: Mixing Weights is now possible in Pose Mode
- Changed: Updater: No longer requires to hover over the buttons in order to update them
- Changed: Updater: Various improvements
- Fixed: A bunch of bugs

#### 0.6.2
- Added: Model: More models are now compatible (please report non working models to us)
- Added: Model: Missing necks are now created automatically
- Changed: Eye tracking: Improved randomness of vertex movement (could fix some instances where the mouth stays open)
- Fixed: Bone Merging: No longer deletes random bones sometimes
- Fixed: Supporter: Names no longer disappear without a reason

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


## Support us
If you enjoy how this plugin saves you countless hours of work consider supporting us through Patreon:

[![](https://i.imgur.com/BFIald5.png)](https://www.patreon.com/catsblenderplugin)