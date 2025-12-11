# Convert image files for TSTO

This package allows you to convert images into rgb/bsv3/bcell assets for the 'The Simpsons: Tapped Out' game.
It uses [**ImageMagick**](https://imagemagick.org/) to perform the conversions and [**sprite-dicing**](https://github.com/elringus/sprite-dicing) under the hood.

**Table of contents**

* [Installation](https://github.com/al1sant0s/tsto2rgb?tab=readme-ov-file#installation)
* [Basic Usage](https://github.com/al1sant0s/tsto2rgb?tab=readme-ov-file#usage)
* [rgb](https://github.com/al1sant0s/tsto2rgb?tab=readme-ov-file#making-rgb-assets)
* [bsv3](https://github.com/al1sant0s/tsto2rgb?tab=readme-ov-file#making-bsv3-assets)
* [bcell](https://github.com/al1sant0s/tsto2rgb?tab=readme-ov-file#making-bcell-assets)
* [Grouping Images](https://github.com/al1sant0s/tsto2rgb?tab=readme-ov-file#grouping-images)
* [Additional Options](https://github.com/al1sant0s/tsto2rgb?tab=readme-ov-file#additional-options)

## Installation

First, make sure you install [**ImageMagick**](https://imagemagick.org/script/download.php) in your system.
You'll also need to install [**python**](https://www.python.org/downloads/)
and [**git**](https://git-scm.com/downloads) if you don't already have them installed.

With everything ready, run either of the following commands in the command-line interface, according to your OS:

* Windows installation command.
```
python -m pip install tsto2rgb@git+https://github.com/al1sant0s/tsto2rgb
```
* Linux installation command.
```
python3 -m pip install tsto2rgb@git+https://github.com/al1sant0s/tsto2rgb
```

If you use Windows, I recommend you get the modern [Windows Terminal from Microsoft Store](https://apps.microsoft.com/detail/9n0dx20hk701?hl).

## Usage

The convert tool will receive a list of directories to search for the image files of specified format, convert them into the necessary files and then
it will save the results in the last directory you provide.

Use the following command to get help with the tool.

```
tsto2rgb --help
```

### Making rgb assets

To create rgb assets, use the --rgb [-r] option and provide a list of directories where the images you want to convert into rgb are located. After that, use the --output [-o] option and provide
where the resulting files will be saved.

```
tsto2rgb -r path/to/images/ -o path/to/rgbs/
```

You can also choose the depth of the image. Use --depth  to choose between 4 (default for in-game sprites) or 8 bits (e.g. a splashscreen) per channel.
The example below uses depth 8, which is useful for creating splashscreen assets.

```
tsto2rgb --depth 8 -r path/to/images/ -o path/to/rgbs/
```


#### Making icon assets

To create menu icon assets, which are basically rgb assets that come in 4 tiers: ipad3, retina, ipad, iphone. Use the --icon [-i] option and
provide a list of directories where the images you want to convert into rgb are located. After that, use the --output [-o] option and provide
where the resulting files will be saved. 4 subfolders will be created within the directory specified under the --output argument. The name will be
determined by the name of the output directory. Take the following command as an example:


```
tsto2rgb -r path/to/icons/ -o path/to/4_70_NewHorizons/
```

This will create the icon assets and save them in the following directories:

* 4_70_NewHorizons:
  * NewHorizonsMenu-ipad3/
  * NewHorizonsMenu-retina/
  * NewHorizonsMenu-ipad/
  * NewHorizonsMenu-iphone/


### Making bsv3 assets

Following the same logic as for making rgb, you will use --bsv [-b] option followed by a list of directories with your buildings, decorations, etc. As before, specify the output directory at the end of the command.

```
tsto2rgb -b path/to/building01/ path/to/building02/ -o path/to/dlc_name/
```

Beware that each directory you provide as an argument to -b option must:

1. represent **only one** entity (i.e., a building or a decoration);
2. follow the specific file structure presented below. **Note! The names used here are just placeholders:**
   * nameofthebuilding/
     * StateNameA/
         * 0.png
         * 1.png
         * ...rest of the image files...
     * StateNameB/
         * 0.png
         * 1.png
         * ...rest of the image files...
     * StateNameC/
         * 0.png
         * 1.png
         * ...rest of the image files...
      * menu.png (optional)
      
3. only contain images that all share the same dimensions (except for the menu.png image, this one should have a smaller size to match the menu). This is quite an important point, and it's necessary to avoid your buildings "wobbling"
   when their animations are shown in game.
4. the images must be named in a way that they are listed in the correct order. You can simply name them with natural numbers if you wish. You can also prepend
   them with a prefix like "frame_" e.g. frame_00.png, frame_01.png, etc.
5. The optional menu.png image must be named exactly like that. If included, the tool will create under the dlc output directory 4 subfolders with the menu rgb file, one for each tier (ipad, ipad3, retina, iphone).

To further elaborate on the previous points, nameofthebuilding will be a directory named with the name of your building (prefer to use non-spaced lowercase names here).
Within the nameofthebuilding directory you should have subdirectories each corresponding to one animation (also called state) your building has.
Within each animation subdirectory, you should actually have the frames for that animation. All the images from all animations subdirectories must convey
to the same dimensions. Think of passing your images like a slideshow, they must be properly aligned to avoid a wobbling effect. Finally, name your frames in a way
that indicates some kind of order. If you name your frames in such a manner that your file explorer software lists them in the desired order, then this is correct.

Usually, when it comes to the animations subdirectories, all buildings have a Neutral animation.
For example, imagine you have a static building, i.e. just one frame, and you decided to call it "Brand New Building" (this is just the formal name).
Here's how you would structure your building:

* brandnewbuilding/
  * Neutral/
    * 0.png
  * menu.png (optional)

So you have a directory named brandnewbuilding. Within that directory you have another directory called Neutral (because your building only has a neutral animation). Finally, you have all your images
for that animation within the Neutral directory itself. In this specific example you would have just one frame that's named 0.png.

Now, for a real and slightly more complex showcase, it's time to demonstrate how to implement a real building in game. For this example, the brown house will be used. The files to reproduce this example
will not be provided by this guide, but you can just reproduce the next steps to any other building/decoration you wish to implement for the game, so pay close attention!

The brown house game file is actually named generichouse01.
The brown house bsv3 file from the game is structured like this (the animations may not be listed in this exact order in the original bsv3 file):

* generichouse01/
  * Active/
     * 0.png
     * 1.png
     * ...rest of the image files...
  * Eggs/
     * 0.png
  * Neutral/
    * 0.png

Without getting into too much details, you will see:

* An animation called "Active" that plays on loop when characters are doing jobs in the brown house. For the brown house, you can see a dimming blue light at the window when this animation is playing;
* The Neutral animation that is actually just one frame, the regular brown house image;
* Eggs is an overlay animation of eggs that covers the brown house. It's currently unused by the game and is just a leftover of previous halloween events.

The brown house is a pretty simple building, but you can find more elaborate buildings in game with additional animations. Take the Simpsons house for example, it contains the following animations:

* simpsonshouse/
  * Active/
  * Active_In/
  * Active_Out/
  * Eggs/
  * Neutral/

* Active_In is an animation that plays once a character, about to do a job at the Simpsons house, reaches it. If the building is currently playing the Neutral animation, the Active_In animation will kick in before
  the Active animation starts. In other words, it is the animation that works as a transition between the Neutral and Active animations.
* Active_Out is an animation that plays once the last character doing a job at the Simpsons house finishes (their thumbs-up icon is tapped by the player). Works as a transition between Active and Neutral animations.

Anyways, continuing with the brown house. Here's a screenshot of the Active subdirectory from my filesystem:

<img width="2050" height="1166" alt="Screenshot_20250920_193341" src="https://github.com/user-attachments/assets/c9218669-edf4-4a30-a5b4-37db70ba48ce" />

Notice how the frames are numbered. That's a way to enforce their correct order as stated before. Now it's time to actually make those images into the required assets for an actual building.
All images here have the same dimensions: 758x601. 

<img width="2050" height="1166" alt="Screenshot_20250923_145618" src="https://github.com/user-attachments/assets/1c8a8e62-51e7-4062-aa4a-b1f0f7c228f0" />

Now, with the following command I run, the corresponding rgb and bsv3 files will be made for the brown house. 

```
tsto2rgb -b Stage/generichouse01/ -o 4_70_NewHorizons/
```

<img width="692" height="451" alt="image" src="https://github.com/user-attachments/assets/73e2c917-bbde-46c2-8d5c-336d54f237ea" />

In this example, I'm saving the newly created assets into the directory of a custom DLC called _4_70_NewHorizons_.

Here are the new files that were made for the brown house. Remember the resulting files will be saved in the subdirectories under the directory you specify with the --output [-o] option:

<img width="728" height="272" alt="image" src="https://github.com/user-attachments/assets/5b56c92a-511e-498b-a7a6-4201c8f1db6e" />

These 3 files will be made for each tier (25, 50, 100). You can find them under the subdirectories bellow the output directory you specified in the call for the command.
If menu.png image was also present, icons will be made for the 4 tiers (ipad3, retina, ipad and iphone).
In the case of this particular example, the assets will be saved under the following subdirectories:

* 4_70_NewHorizons:
  * NewHorizonsBuildDecoGame-100/
  * NewHorizonsBuildDecoGame-50/
  * NewHorizonsBuildDecoGame-25/
  * NewHorizonsMenu-ipad3/    (only if menu.png was present)
  * NewHorizonsMenu-retina/   (only if menu.png was present)
  * NewHorizonsMenu-ipad/     (only if menu.png was present)
  * NewHorizonsMenu-iphone/   (only if menu.png was present)

The image data is located in the rgb and bsv3 files. The third file, called generichouse01.xml, is where to configure the building's characteristics.

> There is one important thing about the last file though. You will not edit the xml file under the output subdirectories. You will edit the xml file that was created
under the input directory. For this example, after the last command has been executed, here it is how the directory structure of **generichouse01** looks like now
>
> * generichouse01/
>  * Active/
>     * 0.png
>     * 1.png
>     * ...rest of the image files...
>  * Eggs/
>     * 0.png
>  * Neutral/
>    * 0.png
>  * **generichouse.xml**


The default configuration of this
file, and for any new building you ever create a bsv3 asset for, it will look like this:

```
<Building x="7" z="5" height="3.5" locX="3" locY="1" transImageX="0.0" transImageY="0.0" offsetX="0" offsetZ="0" depth="4" alpha="1.0" />
```

Here you have several attributes. All attributes except the last 4 are used by the game.
OffsetX, offsetZ, depth and alpha are used by tsto2rgb itself.

Before explaining this line of XML further let's see how the brown house looks in game with the new files.
To actually see those assets in game, it's necessary to pack them as DLC.
You also need to modify the gamescripts to load them for a brand new building (but since the brown house is already registered in game, we don't need to to that). 

I have used **tstodlc** to install the _4_70_NewHorizons_ assets DLC into my local DLC repository. In this case I have set priority to 3000 to override any exisintg assets from the brown house.

```
tstodlc -p3000 4_70_NewHorizons/ ~/Simpsons/dlc/
```

A full explanation of tstodlc is beyond the scope of this guide, so it will not be shown. The focus here is to show how to produce the assets and how to use tsto2rgb to modify the way they look in game.
You can read more about it [here](https://github.com/al1sant0s/tstodlc/).

Here's the _not really new_ brown house.

<img width="2050" height="1166" alt="Screenshot_20250923_143947" src="https://github.com/user-attachments/assets/df697654-9755-4a1b-b331-7099817214f8" />

It looks ok! Let's see it in rearrange mode.

<img width="2050" height="1166" alt="Screenshot_20250923_143730" src="https://github.com/user-attachments/assets/5a8e7a12-0599-42e1-ae7b-b9a218d26ac5" />

Two issues! First, the building itself doesn't lie over the green rectangle. The green rectangle represents the real position of the building, so the sprite should be drawn correctly above it.
Also, you can clearly see how the green rectangle is not shaped correctly to accommodate the whole brown house foundation.
To fix these issues, we need to edit 4 attributes in generichouse01.xml.

Starting with the offsets. The attributes "offsetX" and "offsetZ" define offsets for the position where the sprite will be drawn.
The offsets move the sprite according to the following image:

<img width="2663" height="1385" alt="grid01" src="https://github.com/user-attachments/assets/a605e257-a546-41ed-a908-24615c827091" />

Unfortunately, guessing the correct values is done with trial and error. So at this point it's up to you to throw values in there, rerun the tsto2rgb command to remake the assets and reinstall the DLC with
the new rgb/bsv3/xml files and check how they look in game. Rise and repeat until you end up with a desired result.

In this case, the following values did the trick.

```
<Building x="7" z="5" height="3.5" locX="3" locY="1" transImageX="0.0" transImageY="0.0" offsetX="-0.91" offsetZ="0.59" depth="4" alpha="1.0" />
```

<img width="2050" height="1166" alt="Screenshot_20250923_142541" src="https://github.com/user-attachments/assets/a5f765a5-bd6f-40dc-b777-b91484a5af9a" />

Now, to fix the green rectangle dimensions we need to edit the attributes "x" and "z".

For the brown house, the adequate values are x="5" and z="7".

```
<Building x="5" z="7" height="3.5" locX="1" locY="5" transImageX="0.0" transImageY="0.0" offsetX="-0.91" offsetZ="0.59" depth="4" alpha="1.0" />
```
<img width="2663" height="1385" alt="grid02" src="https://github.com/user-attachments/assets/3c06f07e-9393-49d2-97b7-a3df59bcc7e6" />

and here's how it looks now

<img width="2050" height="1166" alt="Screenshot_20250923_144725" src="https://github.com/user-attachments/assets/a6fe88b2-104f-486c-bd3b-1bec73ab1bbc" />

Perfect! Now just do this for any other building or decoration you have.

Now it's time to quickly explain the remaining attributes:

* height: moves the currency icon above the building vertically. That's where the dollar sign and thumbs-up icons show up above the buildings;
* locX and locY: indicate the position where characters fade out or fade in when they reach a certain position relative to the building. That is when they do jobs on that building.
* transImageX and transImageY are offsets for transimages. You only need to worry about this if you have a file called nameofthebuilding_transimage.rgb in your dlc.

### Making bcell assets

This works really similar to making bsv3 assets. This time you use the --cell [-c] option instead.

```
tsto2rgb -c path/to/character01/ path/to/character02/ -o path/to/bcells/
```
Beware that each directory you provide as an argument to -c option must:

1. represent **only one** entity (i.e., a character or a NPC);
2. follow the specific file structure presented below. **Note! The names used here are just placeholders:**
   * nameofthecharacter/
     * animation_name_a/
         * 0.png
         * 1.png
         * ...rest of the image files...
     * animation_name_b/
         * 0.png
         * 1.png
         * ...rest of the image files...
     * animation_name_c/
         * 0.png
         * 1.png
         * ...rest of the image files...
    * menu.png (optional)
   
3. only contain images that all share the same dimensions (except for the menu.png image, this one should have a smaller size to match the menu). This is quite an important point, and it's necessary to avoid your characters "wobbling"
   when their animations are shown in game.
4. the images must be named in a way that they are listed in the correct order. You can simply name them with natural numbers if you wish. You can also prepend
   them with a prefix like "frame_" e.g. frame_00.png, frame_01.png, etc.
5. The optional menu.png image must be named exactly like that. If included, the tool will create under the dlc output directory 4 subfolders with the menu rgb file, one for each tier (ipad, ipad3, retina, iphone).

To further elaborate on the previous points, nameofthecharacter will be a directory named with the name of your character (prefer to use non-spaced lowercase names here).

Within the nameofthecharacter directory you should have subdirectories each corresponding to one animation your character has.

Within each animation subdirectory, you should actually have the frames for that animation. 

All the images from each animation subdirectory must convey to the same dimensions. Think of passing your images like a slideshow, they must be properly aligned to avoid a wobbling effect. Finally, name your frames in a way
that indicates some kind of order. If you name your frames in such a manner that your file explorer software lists them in the desired order, then this is correct.

Usually, when it comes to the animations subdirectories, all characters have the following animations.

* character/
  * back_walk/
  * front_walk/
  * idle/
  * idle_blink/
  * victory_pose/

For example, here's how Homer Simpson animations could be structured:

* homer/
  * back_walk/
  * front_walk/
  * idle/
  * idle_blink/
  * pick_trash_active/
  * victory_pose/

That is a directory named homer and within that directory you have all animations of that character. After running the command

```
tsto2rgb -c path/to/homer/ -o path/to/dlc_name/
```

the following files will be created:

* rgb files for the frames;

* a bcell file for each animaton of that characater which file name will be made by concatenating the character name with the animation subdirectory name. Take the animation "back_walk" from Homer. The resulting file will
  be called "homer_back_walk.bcell";

* a xml file for each character that lists each of all those characters animations. For the previous the file would be named "homer.xml".

* a xml file for each animation, where you can provide adjustments like offsets and delays between each frame. The name of file will be the same as the ".bcell" file name, except that the extension will be ".xml".
  These files will be saved under the input subdirectories for further editing if necessary.

  For the previous example you would have those new files.

    * homer/
      * back_walk/
        * homer_back_walk.xml
      * front_walk/
        * homer_front_walk.xml
      * idle/
        * homer_idle.xml
      * idle_blink/
        * homer_idle_blink.xml
      * pick_trash_active/
        * homer_pick_trash_active.xml
      * victory_pose/
        * homer_victory_pose.xml
  
  For context here's how these files might look:
  ```
  <AnimSequence offsetX="0" offsetY="0" depth="4">
    <Cell delay="41.666666666666664" />
    <Cell delay="41.666666666666664" />
    <Cell delay="41.666666666666664" />
    <Cell delay="41.666666666666664" />
    <Cell delay="41.666666666666664" />
  </AnimSequence>
  ```
The process after that is analog to the one at the bsv3 section. You pack your new asset files for your character with a DLC,
modify the gamescripts to load your new character, install them into your local DLC repository and check how they look in game.
Then you adjust the offsets and delays for each animation, rerun tsto2rgb to recreate the bcell files, reinstall the DLC with the new files and verify again how they look.
Do that until you end up with the desired results.

Consider the following example:

```
tsto2rgb -c path/to/homer/ -o path/to/_4_70_NewHorizons/
```


The files will be made for each tier (25, 50, 100). You can find them under the subdirectories bellow the output directory you specified in the call for the command.
If menu.png image was also present, icons will be made for the 4 tiers (ipad3, retina, ipad and iphone).
In the case of this particular example, the assets will be saved under the following subdirectories:

* 4_70_NewHorizons:
  * NewHorizonsGame-100/
  * NewHorizonsGame-50/
  * NewHorizonsGame-25/
  * NewHorizonsMenu-ipad3/    (only if menu.png was present)
  * NewHorizonsMenu-retina/   (only if menu.png was present)
  * NewHorizonsMenu-ipad/     (only if menu.png was present)
  * NewHorizonsMenu-iphone/   (only if menu.png was present)


### Grouping images

Set the --group [-g] argument to organise the images in subdirectories within the destination directory.
Each subdirectory corresponds to a certain entity. For example, if there were two image files in 'img_dir', one named
'yellowhouse.png' and the other named 'orangehouse.png', the destination directory would have the following structure after the conversion:

- destination/
  - destination/yellowhouse/
  - destination/orangehouse/

Sometimes an entity also has variations. Suppose, for example there exists 'yellowhouse_normal.png' and 'yellowhouse_premium.png'. Then this would be the resulting directory structure:

- destination/
  - destination/yellowhouse
    - destination/yellowhouse/normal
    - destination/yellowhouse/premium
  - destination/orangehouse
    - destination/orangehouse/_default

In theory, the entity is just the name that precedes the first underscore character in a filename and the variation
is the rest after the underscore, excluding the image extension.
For example, given the name 'something_anything_else.png', _something_ is the entity and _anything_else_ is the variation.
When a file corresponding to an entity doesn't specify a variation (a filename without an underscore in it like 'orangehouse.png') the _default variation subdirectory will be created.

```
tsto2rgb -g -r path/to/Images/ -o path/to/results/
```

## Additional options

You can specify a default depth with the --depth option.

```
tsto2rgb --depth 8 -r path/to/images/ -o path/to/rgbs/
```

You can specify a default alpha with the --alpha [-a] option to use with the bsv3 files. The alpha must be a decimal number between 0.0 (fully transparent) and 1.0 (fully opaque).

```
tsto2rgb -a 1.0 -r path/to/images/ -o path/bsv3s/
```

You can specify a default delay with the --delay [-d] option. The delay can be a decimal number and must be specified in milliseconds terms.

```
tsto2rgb -d 41.68 -r path/to/images/ -o path/bcells/
```
