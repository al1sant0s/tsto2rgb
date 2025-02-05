import argparse
from pathlib import Path
from wand.image import Image
from tsto2rgb.tools.progress import report_progress


def progress_str(n, total, filestem, extension):
    return f"Progress ({n * 100 / total:.2f}%) : [{total - n} file(s) left] ---> {filestem}.{extension}"


# Warning: this script requires ImageMagick to work. If you do not have installed in your system,
# you will have to install it first before using the script.


def main():
    parser = argparse.ArgumentParser(
        description="""
        This tool allows you to convert images back to the raw RGB file format used in the game 'The Simpsons: Tapped Out'.
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
        "--input_extension",
        help="""
        Image format used for the imported images.
        You can choose between most of ImageMagick supported image formats like png, webp, jpg, etc.
        Check ImageMagick documentation for more info about the image formats you can use.
        """,
        default="png",
    )

    parser.add_argument(
        "input_dir",
        help="List of directories containing the image files.",
        nargs="+",
    )

    parser.add_argument(
        "output_dir",
        help="Directory where results will be stored.",
    )

    args = parser.parse_args()
    directories = [Path(item) for item in args.input_dir]

    # Help with the progress report.
    n = 0
    total = 0

    print(f"\n\n--- CONVERTING {args.input_extension.upper()} FILES TO RGB FILES ---\n\n")

    print(
        "Counting the number of files to convert (this might take a while) - ", end=""
    )

    # Get total of files to convert and extract zipped files.

    total = sum(
        [len(list(Path(directory).glob(f"**/*.{args.input_extension}"))) for directory in directories]
    )

    if total == 0:
        print("[No file(s) found!]\n\n")
        print(f"Warning! No {args.input_extension} files found in the specified directories.")
        print("Remember you should specify the directories where the files are, not the files themselves.")
        print("If you need help, execute the following command: tsto2rgb --help\n\n")
        return

    print(f"[{total} file(s) found!]\n\n")

    print(f"--- Starting conversion of {args.input_extension} images ---")

    # Set destination of the converted rgb files.
    target = Path(args.output_dir)
    target.mkdir(exist_ok=True)

    for directory in directories:

        # Process the remaining image files.
        for img_file in directory.glob(f"**/*.{args.input_extension}"):
            n += 1
            report_progress(progress_str(n, total, img_file.stem, args.input_extension), "")

            if args.group is True:
                entity = img_file.stem.split("_", maxsplit=1)

                if len(entity) == 2:
                    target = Path(
                        args.output_dir, entity[0], entity[1].split("_image", maxsplit=1)[0]
                    )
                else:
                    target = Path(args.output_dir, entity[0], "_default")

            else:
                target = Path(args.output_dir)

            target.mkdir(parents=True, exist_ok=True)

            rgb_file = Path(target, f"{img_file.stem}.rgb")

            if args.depth == 4:
                with Image(filename=img_file).fx("u * a", channel="rgb") as tmp_img:
                    width = tmp_img.width
                    height = tmp_img.height

                    # Swap collor channels for 4 bit depth.
                    with Image() as rgb_img:
                        rgb_img.image_add(tmp_img.channel_images["blue"])   # type: ignore
                        rgb_img.image_add(tmp_img.channel_images["alpha"])  # type: ignore
                        rgb_img.image_add(tmp_img.channel_images["red"])    # type: ignore
                        rgb_img.image_add(tmp_img.channel_images["green"])  # type: ignore
                        rgb_img.combine(colorspace="srgb")
                        rgb_img.depth = args.depth
                        rgb_img.format = "rgba"

                        with open(rgb_file, "wb") as binary_file:
                            # Append signature and image dimensions.
                            binary_file.write(int.to_bytes(0, 2, "little"))
                            binary_file.write(int.to_bytes(8192, 2, "little"))
                            binary_file.write(int.to_bytes(width, 2, "little"))
                            binary_file.write(int.to_bytes(height, 2, "little"))

                            # Append rest of the image.
                            binary_file.write(rgb_img.make_blob())  # type: ignore

            elif args.depth == 8:
                with Image(filename=img_file) as rgb_img:
                    width = rgb_img.width
                    height = rgb_img.height

                    rgb_img.depth = args.depth
                    rgb_img.format = "rgba"

                    with open(rgb_file, "wb") as binary_file:
                        # Append signature and image dimensions.
                        binary_file.write(int.to_bytes(0, 2, "little"))
                        binary_file.write(int.to_bytes(0, 2, "little"))
                        binary_file.write(int.to_bytes(width, 2, "little"))
                        binary_file.write(int.to_bytes(height, 2, "little"))

                        # Append rest of the image.
                        binary_file.write(rgb_img.make_blob())  # type: ignore
            else:
                # Ignore this file if it cannot be parsed.
                # Clear line.
                print(150 * " ", end="\r")
                print(f"Invalid {args.input_extension} file. Skipping this file -> {img_file.name}!")
                continue


    print("\n\n--- JOB COMPLETED!!! ---\n\n")
