from wand.image import Image
from pathlib import Path
from tsto2rgb.tools import (
    styles,
    generic_header,
    generic_body,
    generic_footer,
    report_progress,
)


def rgb_parser(main_img, target, depth):


    if main_img.alpha_channel is False:
        main_img.alpha_channel = "opaque"


    if depth == 4:

        width = main_img.width + (main_img.width % 2 > 0)
        height = main_img.height + (main_img.height % 2 > 0)

        with Image(width=width, height=height) as new_img:
            new_img.composite(main_img, 0, 0)

            with new_img.fx("u * a", channel="rgb") as tmp_img:

                width = tmp_img.width
                height = tmp_img.height


                # Swap color channels for 4 bit depth.
                with Image() as rgb_img:
                    rgb_img.image_add(tmp_img.channel_images["blue"])  # type: ignore
                    rgb_img.image_add(tmp_img.channel_images["alpha"])  # type: ignore
                    rgb_img.image_add(tmp_img.channel_images["red"])  # type: ignore
                    rgb_img.image_add(tmp_img.channel_images["green"])  # type: ignore
                    rgb_img.combine(colorspace="srgb")
                    rgb_img.depth = depth
                    rgb_img.format = "rgba"

                    with open(target, "wb") as binary_file:
                        # Append signature and image dimensions.
                        binary_file.write(int.to_bytes(0, 2, "little"))
                        binary_file.write(int.to_bytes(8192, 2, "little"))
                        binary_file.write(int.to_bytes(width, 2, "little"))
                        binary_file.write(int.to_bytes(height, 2, "little"))

                        # Append rest of the image.
                        binary_file.write(rgb_img.make_blob())  # type: ignore
                        return True

    elif depth == 8:
        rgb_img = main_img
        width = rgb_img.width
        height = rgb_img.height

        rgb_img.depth = depth
        rgb_img.format = "rgba"

        with open(target, "wb") as binary_file:
            # Append signature and image dimensions.
            binary_file.write(int.to_bytes(0, 2, "little"))
            binary_file.write(int.to_bytes(0, 2, "little"))
            binary_file.write(int.to_bytes(width, 2, "little"))
            binary_file.write(int.to_bytes(height, 2, "little"))

            # Append rest of the image.
            binary_file.write(rgb_img.make_blob())  # type: ignore
            return True
    else:
        return False


def rgb_gen(files, target, total, input_extension, depth):
    generic_header(styles["rgb"], "rgb", total, input_extension, depth)
    generic_body(styles["rgb"])

    invalid_files = []
    for i in range(total):
        with Image(filename=files[i]) as main_img:
            status = rgb_parser(main_img, Path(target, files[i].stem + ".rgb"), depth)
            report_progress(
                f" * Progress: {(i + 1) * 100 // total:3d}% -> {files[i].stem}.{input_extension}",
                "",
                styles["normal"],
            )
            if status is False:
                invalid_files.append(files[i].name)

    generic_footer(styles["rgb"], total, invalid_files)
