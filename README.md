# Convert image files to RGB/BSV3/BCELL files for TSTO

This package allows you to convert images into RGB/BSV3/BCELL assets for the 'The Simpsons: Tapped Out' game.
It uses [**ImageMagick**](https://imagemagick.org/) to perform the conversions and (**sprite-dicing**)[https://github.com/elringus/sprite-dicing] under the hood.

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

If you use windows I recommend you to get the modern [windows terminal from microsoft store](https://apps.microsoft.com/detail/9n0dx20hk701?hl).

## Usage

The convert tool will receive a list of directories to search for the image files of specified format, convert them into the necessary files and then
it will save the results in the last directory you provide.

Use the following command to get help with the tool.

```
tsto2rgb --help
```

### Making RGB assets

To create rgb assets use the --rgb [-r] option and provide a list of directories where the images you want to convert into rgb are located. After that, use the --output [-o] option and provide
where the resulting files will be saved into.

```
tsto2rgb -r /path/to/images -o /path/to/new-rgb-images/
```

You can also choose the depth of the image. Use --depth [-d] to choose between 4 (default for in-game sprites) or 8 bits (e.g. a splashscreen) per channel.
The example bellow uses depth 8 which is useful for creating splashscreen assets.

```
tsto2rgb -d 8 -r /path/to/images -o /path/to/new-rgb-images/
```

### Making BSV3 assets

Following with the same logic as for making rgb, you will use --bsv [-b] option followed by a list of directories with your buildings, decorations, etc. As before specify the output directory at the end of the command.

```
tsto2rgb -b /path/to/building01 /path/to/building02 -o /path/to/new-bsv/
```

Beware that each directory you provide as an argument -b option option must
be associated with **only one** entity (i.e., a building or a decoration). They also must follow the following structure. Note! The names used bellow are placeholders.

* nameofthebuilding/
  * StateNameA/
      * 0.png
      * 1.png
      * ...rest of the image files...
  * StateNameB/
  * StateNameC/

That is, nameofthebuilding will be a directory named with the name of your building (prefer to use non spaced lowercase names here).
Within nameofthebuilding directory you should have subdirectories each corresponding to one animation (also called state) your building has. 

Usually all buildings have a Neutral animation. For example, imagine you have a static building i.e. just one frame (no animations), and you decided to call it "Brand New Building" (this is just the formal name).
Here's how you would structure your building:

* brandnewbuilding/
  * Neutral/
    * 0.png

So you have a directory named brandnewbuilding. Within that directory you have another directory called Neutral (because your building only has a neutral animation). Finally you have all your images
for that animation within the Neutral directory itself. In this specific example you would have one frame that's named 0.png.

Now for a real example. Suppose you have been tasked with implementing the "Simpsons House". I know! That building already exists in the game but let's pretend it doesn't (as strange as it sounds).
Taking the real Simpsons house asset from the game you will find out that it's structured like this (the states may not be in this exactly order in the original bsv3 file):

* simpsonshouse/
  * Active/
  * Active_In/
  * Active_Out/
  * Eggs/
  * Neutral/

Without getting into too much details, you will see:

* An animation called "Active" that plays on loop when characters are doing jobs in the simpsons house;
* The Neutral animation that is actually just one frame (the regular simpsons house with the closed windows);
* Active_In is an animation that plays once a character, about to do a job at the Simpsons house, reaches it. If the building is currently playing the Neutral animation, the Active_In animation will be played before
  the Active animation starts. In other words is the animation that works as a transition between the Neutral and Active animations.
* Active_Out is an animation that plays once the last character doing a job at the Simpsons house finishes (their thumbs-up icon is tapped by the player). Works as a transition between Active and Neutral animations.
* Eggs is an overlay animation of eggs that covers the Simpsons house. It's currently unused by the game and is just a leftover of previous halloween events.

Here's an screenshot of the Active subdirectory from my filesystem:

<img width="2050" height="1166" alt="img-house" src="https://github.com/user-attachments/assets/7af9c6c8-ffeb-40d7-8b44-bc03d8b5e5bc" />

Notice how the frames are numbered. That's a way to enforce their correct order. Now it's time to actually make those images into the required assets for an actual building. Confirming the strucuture above,
here's how the files should be stuctured.

<img width="1915" height="296" alt="image" src="https://github.com/user-attachments/assets/7e99c213-f43d-4fd9-9b20-f493cf1970ad" />


Now with the folowing command I run, the corresponding rgb and bsv3 files will be made for the Simpsons house. 

```
tsto2rgb -b Stage/simpsonshouse/ -o 4_70_NewHorizons/NewHorizons-BuildDecoGame-100/
```

<img width="730" height="431" alt="image" src="https://github.com/user-attachments/assets/3e85b02c-2707-4004-96b8-b9377a51001a" />

In this example I'm saving the new created assets into the directory of a custom DLC called _4_70_NewHorizons_. To actually see those assets in game it's necessary to pack them as DLC and
modify the gamescripts to load them. The way to do this is way beyond the scope of this guide so it will not be shown. The focus here is to produce the assets and how to use the tsto2rgb to modify the way they look in game.

With that said, here are the new files that were made for the Simpsons house:

<img width="815" height="298" alt="image" src="https://github.com/user-attachments/assets/c1927350-e56d-4bc1-a5de-0979f4e40df9" />

The image data is located in the rgb and bsv3 files. The 3rd file called simpsonshouse.xml is where you will configure your buildings characteristics. The default configuration of this
file and for any new building you create a bsv3 asset for will looks like this

```
<Building x="5" z="5" height="3.5" locX="1" locY="5" transImageX="0.0" transImageY="0.0" offsetX="0" offsetZ="0" depth="4" alpha="255" />
```

Here you have several attributes. All attributes, except the last 4 attributes, are used by the game.
OffsetX, offsetZ, depth and alpha are used by tsto2rgb itself.

Before explaing this line of xml furhter let's see how the Simpsons house looks in game. After doing the necessary modifications in gamescripts and have used [tstodlc](https://github.com/al1sant0s/tstodlc/) to install the _4_70_NewHorizons_ DLC into my local gameserver DLC repository. Here's the _not really_ new Simpsons house in game.

<img width="2050" height="1166" alt="image" src="https://github.com/user-attachments/assets/9195916b-9dd0-42cd-a50f-d25bb7a845b5" />

Lots of wrong things here. First the building itself doesn't lay onto that green rectangle. The green rectangle represents the real position of the building so the sprite should be drawn correctly above it.





## Multiple directories

An example specifying multiple directories as input and saving the results in the assets directory.

```
tsto2rgb path/to/Downloads/img_files path/to/Images/img_folder path/to/Images/another_img_folder path/to/assets
```

If you want to search for the image files recursively in every subdirectory bellow a specific directory, give the root directory as input. The following example will convert all the image files within the 'Images' directory,
including the 'img_folder' and 'another_img_folder' subdirectories.

```
tsto2rgb path/to/Downloads/img_files path/to/Images path/to/assets
```

## Grouping images

Set the --group argument to organize the images in subdirectories within the destination directory.
Each subdirectory corresponds to a certain entity. For example, if there were two image files in 'img_dir', one named
'yellowhouse.png' and the other named 'orangehouse.png', the destination directory would have the following structure after the conversion:

- destination/
  - destination/yellowhouse/
  - destination/orangehouse/

Sometimes an entity also has variations. Suppose for example there exists 'yellowhouse_normal.png' and 'yellowhouse_premium.png'. Then this would be the resulting directory structure:

- destination/
  - destination/yellowhouse
    - destination/yellowhouse/normal
    - destination/yellowhouse/premium
  - destination/orangehouse
    - destination/orangehouse/_default

In theory, the entity is just the name that precedes the first underscore character in a filename and the variation
is the rest after the underscore excluding the image extension.
For example, given the name 'something_anything_else.png', _something_ is the entity and _anything_else_ is the variation.
When a file corresponding to an entity doesn't specify a variation (a filename without an underscore in it like 'orangehouse.png') the _default variation subdirectory will be created.

```
tsto2rgb --group path/to/Images path/to/assets
```
