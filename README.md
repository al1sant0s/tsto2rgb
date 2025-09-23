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

### Making bsv3 assets

Following the same logic as for making rgb, you will use --bsv [-b] option followed by a list of directories with your buildings, decorations, etc. As before, specify the output directory at the end of the command.

```
tsto2rgb -b path/to/building01/ path/to/building02/ -o path/to/bsv3s/
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
3. only contain images that all share the same dimensions. This is quite an important point, and it's necessary to avoid your buildings "wobbling"
   when their animations are shown in game.
4. the images must be named in a way that they are listed in the correct order. You can simply name them with natural numbers if you wish. You can also prepend
   them with an preffix like "frame_" e.g. frame_00.png, frame_01.png, etc.

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

So you have a directory named brandnewbuilding. Within that directory you have another directory called Neutral (because your building only has a neutral animation). Finally, you have all your images
for that animation within the Neutral directory itself. In this specific example you would have just one frame that's named 0.png.

Now, for a real and slightly more complex showcase, it's time to demonstrate how to implement a real building in game. For this example, the brown house will be used. The files to reproduce this example
will not be provided by this guide, but you can just reproduce the next steps to any other building/decoration you wish to implement for the game, so pay close attention!

The brown house game file is actually named generichouse01.
The brown house bsv3 file from the game is structured like this (the animations may not be listed in this exact order in the original bsv3 file):

* generichouse01/
  * Active/
  * Eggs/
  * Neutral/

Without getting into too much detail, you will see:

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

* Active_In is an animation that plays once a character, about to do a job at the Simpsons house, reaches it. If the building is currently playing the Neutral animation, the Active_In animation will be played before
  the Active animation starts. In other words, it is the animation that works as a transition between the Neutral and Active animations.
* Active_Out is an animation that plays once the last character doing a job at the Simpsons house finishes (their thumbs-up icon is tapped by the player). Works as a transition between Active and Neutral animations.

Anyways, continuing with the brown house. Here's a screenshot of the Active subdirectory from my filesystem:

<img width="2050" height="1166" alt="Screenshot_20250920_193341" src="https://github.com/user-attachments/assets/c9218669-edf4-4a30-a5b4-37db70ba48ce" />

Notice how the frames are numbered. That's a way to enforce their correct order as stated before. Now it's time to actually make those images into the required assets for an actual building. Confirming the structure above,
here's how the files should be structured.

<img width="817" height="301" alt="image" src="https://github.com/user-attachments/assets/044d8d25-01d0-41d3-8baf-df4e2aab8aac" />

All images here have the same dimensions: 758x601. 

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/53b315f1-7f55-4c7a-90ca-74642656eeac" />

Now, with the following command I run, the corresponding rgb and bsv3 files will be made for the brown house. 

```
tsto2rgb -b Stage/generichouse01/ -o 4_70_NewHorizons/NewHorizons-BuildDecoGame-100/
```

<img width="692" height="451" alt="image" src="https://github.com/user-attachments/assets/73e2c917-bbde-46c2-8d5c-336d54f237ea" />


In this example, I'm saving the newly created assets into the directory of a custom DLC called _4_70_NewHorizons_. To actually see those assets in game, it's necessary to pack them as DLC and
modify the gamescripts to load them. The way to do this is beyond the scope of this guide, so it will not be shown. The focus here is to show how to produce the assets and how to use tsto2rgb to modify the way they look in game.

With that said, here are the new files that were made for the brown house. Remember the resulting files will be saved in the directory you specify with the --output [-o] option:

<img width="728" height="272" alt="image" src="https://github.com/user-attachments/assets/5b56c92a-511e-498b-a7a6-4201c8f1db6e" />

The image data is located in the rgb and bsv3 files. The third file, called generichouse01.xml, is where to configure the building's characteristics. The default configuration of this
file, and for any new building you ever create a bsv3 asset for, it will look like this:

```
<Building x="5" z="5" height="3.5" locX="1" locY="5" transImageX="0.0" transImageY="0.0" offsetX="0" offsetZ="0" depth="4" alpha="1.0" />
```

Here you have several attributes. All attributes except the last 4 are used by the game.
OffsetX, offsetZ, depth and alpha are used by tsto2rgb itself.

Before explaining this line of XML further let's see how the brown house looks in game with the new files. After doing the necessary modifications in gamescripts, I have used [tstodlc](https://github.com/al1sant0s/tstodlc/) to install the _4_70_NewHorizons_ DLC into my local gameserver DLC repository. Here's the _not really new_ brown house.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7ac2d767-6b40-45ca-a1ca-e028fccccc93" />

Not bad, right?! Let's see it in rearrange mode.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/61358efe-7625-4f5b-9999-0cbc1dc2e0f2" />

Two issues! First, the building itself doesn't lie over that green rectangle. The green rectangle represents the real position of the building, so the sprite should be drawn correctly above it.
Also, you can clearly see how the green rectangle is not big enough to accommodate the whole brown house foundation.

> Before you say it's a square. Yes! I know it is a square. I'm referring to it as a rectangle because most of the time your building will have a rectangular shape. Also, a square is just a special case of a rectangle.

To fix this, we need to edit 4 attributes in generichouse01.xml. The attributes "x" and "z" control the dimensions of the green rectangle, whereas "offsetX" and "offsetZ" define offsets for the position where the sprite will be drawn.
Our mission here is to come up with the appropriate values for those 4 attributes so the building lies on a correctly sized green rectangle when selected in rearrange mode (the mode where you move buildings in game).

Let's start by resizing the green rectangle. In this case, the adequate values are x="5" and z="7".

```
<Building x="5" z="7" height="3.5" locX="1" locY="5" transImageX="0.0" transImageY="0.0" offsetX="0" offsetZ="0" depth="4" alpha="1.0" />
```
and here's how it looks in game now

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/d483445d-f34f-47de-8c3f-90b78ed9b5bf" />

Much better, right?! Now, to fix the offsets by editing "offsetX" and "offsetZ" attributes so the house appears above the rectangle.
Each offset attribute moves with positive values according to the following axes:

<img width="2544" height="1385" alt="final_grid" src="https://github.com/user-attachments/assets/58b7543c-79ed-493b-b76e-506c5a81ef4f" />

Unfortunately, guessing the correct values is done with trial and error. So at this point it's up to you to throw values in there, rerun the tsto2rgb command to remake the assets and reinstall the DLC with
the new rgb/bsv3/xml files and check how they look in game. Rise and repeat until you end up with a desired result. Also when reruning tsto2rgb command it's quite important
that you point it to save to the same place where your current resulting rgb/bsv3/xml files are because it will retrieve the offsets and other attributes from there and embed them into the newest bsv3 file.

In this case, the following values did the trick.

```
<Building x="5" z="7" height="3.5" locX="1" locY="5" transImageX="0.0" transImageY="0.0" offsetX="0.215" offsetZ="0.125" depth="4" alpha="1.0" />
```

and here's how it looks now

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7da00908-5252-451f-8a7e-fa3a87def700" />

Perfect! Now just do this for any other building or decoration you have.

Now it's time to quickly explain the remaining attributes:

* height: moves the currency icon above the building vertically. That's where the dollar sign and thumbs-up icons show up above the buildings;
* locX and locY: indicate the position where characters fade out or fade in when they reach a certain position relative to the building. That is when they do jobs on that building.
  locX and locY here are the usual cartesian x and y axes, to not be confused with the x axis of offsetX;
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
3. within each animation subdirectory only contain images that all share the same dimensions. This is quite an important point, and it's necessary to avoid your characters "wobbling"
   when their animations are shown in game.
4. the images must be named in a way that they are listed in the correct order. You can simply name them with natural numbers if you wish. You can also prepend
   them with an preffix like "frame_" e.g. frame_00.png, frame_01.png, etc.

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

That is a directoy named homer and within that directory you have all animations of that character. After running the command

```
tsto2rgb -c path/to/homer/ -o path/to/homer_assets/
```

the following files will be created for each animation:

* a bcell file for each animaton of that characater which file name will be made by concatenating  the character name with the animation subdirectory name. Take the animation "back_walk" from Homer. The resulting file will
  be called "homer_back_walk.bcell";

* a xml file for each animation, where you can provide adjustments like offsets and delays between each frame. The nam of file will be the same as the ".bcell" file name, except that the extension will be ".xml".  For the previous example you would have "homer_back_walk.xml". For context here's how this file might look:
```
<AnimSequence offsetX="0" offsetY="0" depth="4">
  <Cell delay="41.666666666666664" />
  <Cell delay="41.666666666666664" />
  <Cell delay="41.666666666666664" />
  <Cell delay="41.666666666666664" />
  <Cell delay="41.666666666666664" />
</AnimSequence>
```

* a xml file for each character that lists each all those characters animations. For the previous the file would be named "homer.xml".

The process after that is the analog to the one at the bsv3 section. You pack your new asset files for your character with a DLC,
modify the gamescripts to load your new character, install them into your server DLC repository and check how they look in game.
Then you adjust the offsets and delays for each animation, rerun tsto2rgb to recreate the bcell files, reinstall the DLC with the new files and verify again how they look.
Do that until you end up with the desired results.

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
