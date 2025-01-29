# Convert image files to RGB files for TSTO

This package allows you to convert images into RGB assets for the 'The Simpsons: Tapped Out' game.
It uses [**ImageMagick**](https://imagemagick.org/) to perform the conversions.

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

## Usage

```
tsto2rgb --help
```

The convert tool will receive a list of directories to search for the image files of specified format, convert them into rgb files and then
it will save the results in the last directory you provide. For example, supposing the image files are inside a directory called 'img_dir' and you want the images to be exported to the 'destination' directory, you would issue the following command:

```
tsto2rgb path/to/img_dir path/to/destination
```
## Arguments

If you prefer to use a different type of image instead of png, you can use the --input_extension argument.

```
tsto2rgb --input_extension webp path/to/img_dir path/to/destination
```

You can also choose the depth of the image. Choose between 4 (default) or 8 bits per channel.

```
tsto2rgb --depth 8 path/to/img_dir path/to/destination
```

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
