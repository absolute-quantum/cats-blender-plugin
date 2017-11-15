# cats-blender-plugin

A tool designed to shorten steps needed to import and optimise MMD models into VRChat

## Features
 - Creating texture atlas
 - Creating mouth visemes
 - Creating eye tracking

*More to come!*

## Installation
1. copy the script: [cats.py](https://raw.githubusercontent.com/michaeldegroot/cats-blender-plugin/master/cats.py)
2. paste the script into your text editor of blender like so: 

![](https://i.imgur.com/UTsjtWy.gif)

3. Check your 3d view and there should be a new menu item called **CATS** ....w00t

## Texture atlas
![](https://i.imgur.com/ht7D3cK.png)

**Texture atlas is the process of combining multiple textures into one to save processing power to render one's model**
If you are unsure about what to do with the margin and angle setting, then leave it default. The most important setting here is texture size and target mesh.

### Properties

##### Margin
Margin to reduce bleed of adjacent islands

##### Angle
Lower for more projection groups, higher for less distortion

##### Texture size
Lower for faster bake time, higher for more detail.

##### Target mesh
The mesh that you want to create a atlas from

##### Disable multiple textures
Texture baking and multiple textures per material can look weird in the end result. Check this box if you are experiencing this.
**If any experienced blender user can tell me how to fix this more elegantly please do let me know!**

## Mouth visemes
![](https://i.imgur.com/3fCSjYK.png)

**Mouth visemes are used to show more realistic mouth movement in-game when talking over the microphone**
The script generates 17 shape keys from the 3 shape keys you specified. It uses the mouth visemes A, OH and CH to generate this output. 
*This is still a experimental feature and will be fine tuned over the course of time*

### Properties

##### Mesh
The mesh with the mouth shape keys

##### Viseme A
The name of the shape key that controls the mouth movement that looks like someone is saying A

##### Viseme OH
The name of the shape key that controls the mouth movement that looks like someone is saying OH

##### Viseme CH
The name of the shape key that controls the mouth movement that looks like someone is saying CH

## Eye tracking
![](https://i.imgur.com/LPlF6wQ.png)

**Eye tracking is used to artificially track someone when they come close to you**
It's important to note that the left eye and right eye bones need to be weight painted to each of their eye bone respectively. 
It's also a good idea to check the eye movement in pose mode after this operation to check the validity of the automatic eye tracking creation.

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

##### Experimental eye fix
Script will try to verify the newly created eye bones to be located in the correct position, this works by checking the location of the old eye vertex group. It is very useful for models that have over-extended eye bones that point out of the head

## Roadmap
 - Armature fixing (naming, parenting, weighting)

## Feedback
Send your feedback to this discord server https://discord.gg/up9Zqsu and look for givemeallyourcats ;)
