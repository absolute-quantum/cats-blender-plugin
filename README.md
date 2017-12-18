# Cats Blender Plugin (0.4.0)

A tool designed to shorten steps needed to import and optimize MMD models into VRChat

Development branch: ![](https://api.travis-ci.org/michaeldegroot/cats-blender-plugin.svg?branch=development)

Master branch: ![](https://api.travis-ci.org/michaeldegroot/cats-blender-plugin.svg?branch=master)

[![](https://i.imgur.com/BFIald5.png)](https://www.patreon.com/catsblenderplugin)

## Features
 - Optimizing armature with one click!
 - Creating mouth visemes
 - Creating eye tracking
 - Creating texture atlas
 - Creating root bones for Dynamic Bones
 - Optimizing materials
 - Translating shape keys, bones, materials and meshes
 - Auto updater

*More to come!*

## Installation
 - download the plugin: [Cats Blender Plugin](https://github.com/michaeldegroot/cats-blender-plugin/archive/master.zip)

 - Install the the addon in blender like so:

![](https://i.imgur.com/eZV1zrs.gif)

 - Check your 3d view and there should be a new menu item called **CATS** ....w00t

![](https://i.imgur.com/ItJLtNJ.png)

 - If you need help figuring out how to use the tool:

[![VRChat - Cat's Blender Plugin Overview](https://img.youtube.com/vi/0gu0kEj2xwA/0.jpg)](https://www.youtube.com/watch?v=0gu0kEj2xwA)


## Code contributors:
 - Hotox
 - Shotariya
 - Neitri


## Model
![](https://i.imgur.com/gw66CMj.png)

A vastly improved combination of Neitri and Shotariya's blender plugins, it tries to fix and optimize the armature with one click.

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
Imports a mmd model (.pmx, .pmd). This requires mmd_tools in order to work.

##### Separate by material
Separatres a mesh by materials

##### Join meshes
Joins all meshes into one

##### Mix weights
Deletes the selected bones and adds their weight to their respective parents.


## Translation

![](https://i.imgur.com/SCyhVn1.png)

**Can translate certain entities from any language to english** Works by sending a request to the Google translate service. This feature can be slow for entities with a large amount of items.


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


## Update Plugin
There is an auto updater in the plugin so you don't have to keep checking for new version. This is how to check for updates:

![](https://i.imgur.com/LbO7Xst.gif)


## Changelog

#### 0.4.0
- Added: Model: A lot more models are now compatible (if not please report it to us)
- Added: Bone Merging: A new feature that can reduce huge groups of bones (useful for Dynamic Bones)
- Added: Model: Mixamo models are now fixable!
- Added: Progress notification on serveral operations
- Added: Model: Joining meshes now applies all unapplied decimation modifiers
- Added: Model: New "Start/Stop Pose Mode" button
- Changed: Functions that need UI context are now excluded from the spacebar menu
- Changed: Separate by Materials: Improved search for the mesh
- Fixed: Undo now works better
- Fixed: Bugs, bugs and bugs

#### 0.3.0
- Added: Armature: More models are now compatible (if not please report it to us)
- Added: Armature: Fix hips now adjusts the upper leg bones to be placed more correctly for full body tracking
- Added: Eye Tracking: Testing of blink and lowerlid shapes
- Added: UI: Custom icons!
- Added: Armature: Added "Import Model" button (shortcut to the mmd_tools button)
- Added: Armature: Added "Separate by Materials" button (shortcut to the mmd_tools button)
- Added: Armature: Fixing Armature now correctly sets the shading
- Added: Updater: New popup when update is available
- Changed: Eye Tracking: Made "Basis" usable again (useful for models with a single shape containing both blinks)
- Changed: Armature Panel renamed to Model
- Fixed: Optimization: Combine same materials now ignores inactive texture slots in it's unique identification
- Fixed: Armature: Fixed multiple toes bug
- Fixed: Even more bugs

#### 0.2.1
- Added: Supporters (donators) tab
- Fixed: Atlas: Alpha values are restored after atlassing (thanks Tupper!)
- Fixed: Combine Meshes: Error 'NoneType attribute has no key_blocks' fixed
- Fixed: Combine Materials: Now also checks for uniqueness on specular and diffuse color

See the full changelog [here](https://github.com/michaeldegroot/cats-blender-plugin/releases).


## Roadmap
 - MOAR updates on the armature code
 - Texture translation should have an option to rename the filename also
 - Automatic lower lid creation for eye tracking
 - Manual bone selection button for root bones


## Feedback
Do you love this plugin or have you found a bug?
Post a response in this thread or send your feedback to the official discord server of the plugin for real-time communication: https://discord.gg/f8yZGnv and look for people with the developer role ;)
