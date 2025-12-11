import argparse
from pathlib import Path
from colorama import init
from tsto2rgb.tools import styles, colorprint
from tsto2rgb.parsers import rgb_gen, bsv_gen, bcell_gen


# Warning: this script requires ImageMagick to work. If you do not have installed in your system,
# you will have to install it first before using the script.


def main():
    init()

    parser = argparse.ArgumentParser(
        description="""
        This tool allows you to convert images to rgb, bsv3 and bcell custom formats for usage in the game 'The Simpsons: Tapped Out'.
        It uses ImageMagick to perform the conversions, so make sure you have it installed in your system.
        Multiple options are available for customizing the results. You can choose the file extension of the input images, where to save it, etc.
        Check the help for more information.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--group",
        help="If this option is enabled, the files will be separated into subfolders within the output directory.",
        action="store_true",
    )

    parser.add_argument(
        "--depth",
        help="Depth used for the image (choose between 4 and 8 bits per channel).",
        default=4,
        type=int,
    )

    parser.add_argument(
        "-a",
        "--alpha",
        help="Alpha used for the bsv assets (0.0-1.0).",
        default=1.0,
        type=float,
    )

    parser.add_argument(
        "-d",
        "--delay",
        help="""
        Delay in miliseconds used for the frames in a new bcell asset. This value will only
        be used if there is no cell.xml file within the source image directory.
        """,
        default=1000 / 24,
        type=float,
    )

    parser.add_argument(
        "-e",
        "--input_extension",
        help="""
        Image format used for the imported images.
        You can choose between most of ImageMagick supported image formats like png, webp, jpg, etc.
        Check ImageMagick documentation for more info about the image formats you can use.
        """,
        default="png",
    )

    parser.add_argument(
        "-r",
        "--rgb",
        help="List of directories containing image files to be converted into rgb files.",
        nargs="+",
    )


    parser.add_argument(
        "-i",
        "--icon",
        help="""
        List of directories containing image files to be converted into rgb files. This option will produce 4 variants of each image,
        one for each tier which are: ipad3, ipad, retina and iphone.
        """,
        nargs="+",
    )


    parser.add_argument(
        "-s",
        "--splash",
        help="""
        List of directories containing image files to be converted into rgb files. This option will produce 3 variants of each image,
        one for each tier of a splash which are: small, medium and large. It will also use 8 bit depth by default.
        """,
        nargs="+",
    )


    parser.add_argument(
        "-b",
        "--bsv",
        help="List of directories containing subdirectories containing image files to be converted into rgb and bsv3 files.",
        nargs="+",
    )

    parser.add_argument(
        "-c",
        "--bcell",
        help="List of directories containing subdirectories containing image files to be converted into rgb and bcell files.",
        nargs="+",
    )


    parser.add_argument(
        "-o", "--output", help="Directory where results will be stored.", required=True
    )

    args = parser.parse_args()

    # Get all directories.
    rgb_files = (
        [
            Path(item).resolve()
            for item in args.rgb
            if Path(item).resolve().is_dir() is True
            and Path(item).resolve().name not in ("", ".", "..")
        ]
        if args.rgb is not None
        else []
    )
    rgb_files = [
        Path(directory).glob(f"*.{args.input_extension}") for directory in rgb_files
    ]
    rgb_files = [file for glob in rgb_files for file in glob]


    icon_files = (
        [
            Path(item).resolve()
            for item in args.icon
            if Path(item).resolve().is_dir() is True
            and Path(item).resolve().name not in ("", ".", "..")
        ]
        if args.icon is not None
        else []
    )
    icon_files = [
        Path(directory).glob(f"*.{args.input_extension}") for directory in icon_files
    ]
    icon_files = [file for glob in icon_files for file in glob]


    bsv_directiores = (
        [
            Path(item).resolve()
            for item in args.bsv
            if Path(item).resolve().is_dir() is True
            and Path(item).resolve().name not in ("", ".", "..")
        ]
        if args.bsv is not None
        else []
    )

    bcell_directiories = (
        [
            Path(character).resolve()
            for character in args.bcell
            if Path(character).resolve().is_dir() is True
            and Path(character).resolve().name not in ("", ".", "..")
        ]
        if args.bcell is not None
        else []
    )

    # Help with the progress report.
    n = 0

    # Get total of files to convert.

    rgb_total = len(rgb_files)
    icon_total = len(icon_files)
    bsv_total = len(bsv_directiores)
    bcell_total = len(bcell_directiories)

    # Check if there's any work to do.
    if rgb_total + icon_total + bsv_total + bcell_total == 0:
        colorprint(styles["normal"], "\n\n [!] [No file(s) found!]\n\n")
        colorprint(
            styles["normal"],
            f" [*] Warning! No {args.input_extension} files found in the specified directories.",
        )
        colorprint(
            styles["normal"],
            " [*] Remember you should specify the directories where the files are, not the files themselves.",
        )
        colorprint(
            styles["normal"],
            " [*] If you need help, execute the following command: tsto2rgb --help\n\n",
        )
        return

    # Procede with operation.
    if rgb_total + icon_total > 0:
        target = Path(args.output)
        target.mkdir(parents=True, exist_ok=True)
        rgb_gen(rgb_files, icon_files, target, args.input_extension, args.depth)


    if bsv_total > 0:
        target = Path(args.output)
        target.mkdir(parents=True, exist_ok=True)
        bsv_gen(
            bsv_directiores,
            target,
            bsv_total,
            args.input_extension,
            args.depth,
            args.alpha,
        )

    if bcell_total > 0:
        target = Path(args.output)
        target.mkdir(parents=True, exist_ok=True)
        bcell_gen(
            bcell_directiories,
            target,
            bcell_total,
            args.input_extension,
            args.depth,
            args.delay,
        )

    #    if total == 0:
    #        print("[No file(s) found!]\n\n")
    #        print(f"Warning! No {args.input_extension} files found in the specified directories.")
    #        print("Remember you should specify the directories where the files are, not the files themselves.")
    #        print("If you need help, execute the following command: tsto2rgb --help\n\n")
    #        return

    #    # Set destination of the converted rgb files.
    #    target = Path(args.output_dir)
    #    target.mkdir(exist_ok=True)
    #
    #    for directory in directories:
    #
    #        # Process the remaining image files.
    #        for img_file in directory.glob(f"**/*.{args.input_extension}"):
    #            n += 1
    #            report_progress(progress_str(n, total, img_file.stem, args.input_extension), "")
    #
    #            if args.group is True:
    #                entity = img_file.stem.split("_", maxsplit=1)
    #
    #                if len(entity) == 2:
    #                    target = Path(
    #                        args.output_dir, entity[0], entity[1].split("_image", maxsplit=1)[0]
    #                    )
    #                else:
    #                    target = Path(args.output_dir, entity[0], "_default")
    #
    #            else:
    #                target = Path(args.output_dir)
    #
    #            target.mkdir(parents=True, exist_ok=True)

    print("\n\n--- JOB COMPLETED!!! ---\n\n")
