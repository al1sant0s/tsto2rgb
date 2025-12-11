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



def make_icons(icon_img, target, filename):

    status = True

    with Image(image = icon_img) as img:
        subtarget = Path(target, target.name.split("_")[-1] + "Menu-ipad3")
        subtarget.mkdir(exist_ok = True)
        status = status and rgb_parser(img, Path(subtarget, filename), 4)


    with Image(image = icon_img) as img:
        subtarget = Path(target, target.name.split("_")[-1] + "Menu-retina")
        subtarget.mkdir(exist_ok = True)
        img.resize(width = int(img.width * 2 / 3), height = int(img.height * 2 / 3))
        status = status and rgb_parser(img, Path(subtarget, filename), 4)


    with Image(image = icon_img) as img:
        subtarget = Path(target, target.name.split("_")[-1] + "Menu-ipad")
        subtarget.mkdir(exist_ok = True)
        img.resize(width = int(img.width / 2), height = int(img.height / 2))
        status = status and rgb_parser(img, Path(subtarget, filename), 4)


    with Image(image = icon_img) as img:
        subtarget = Path(target, target.name.split("_")[-1] + "Menu-iphone")
        subtarget.mkdir(exist_ok = True)
        img.resize(width = int(img.width * 1 / 3), height = int(img.height * 1 / 3))
        status = status and rgb_parser(img, Path(subtarget, filename), 4)


    return status


def rgb_gen(rgb_files, icon_files, target, input_extension, depth):


    rgb_total = len(rgb_files)
    icon_total = len(icon_files)
    splash_total = 0
    total = rgb_total + icon_total + splash_total

    generic_header(styles["rgb"], "rgb", total, input_extension, depth)
    generic_body(styles["rgb"])


    invalid_files = []


    # Normal rgb files.
    for i in range(rgb_total):
        with Image(filename=rgb_files[i]) as main_img:
            status = rgb_parser(main_img, Path(target, rgb_files[i].stem + ".rgb"), depth)
            report_progress(
                f" * Progress: {(i + 1) * 100 // rgb_total:3d}% -> {rgb_files[i].stem}.{input_extension}",
                "",
                styles["normal"],
            )
            if status is False:
                invalid_files.append(rgb_files[i].name)


    # Icon files.
    for i in range(icon_total):
        with Image(filename=icon_files[i]) as icon_img:
            status = make_icons(icon_img, target,  icon_files[i].stem + ".rgb")
            report_progress(
                f" * Progress: {(i + 1) * 100 // icon_total:3d}% -> {icon_files[i].stem}.{input_extension}",
                "",
                styles["normal"],
            )
            if status is False:
                invalid_files.append(icon_files[i].name)



    generic_footer(styles["rgb"], total, invalid_files)
