import numpy as np
import xml.etree.ElementTree as ET
from natsort import natsorted
from wand.image import Image
from pathlib import Path
from tsto2rgb.parsers.rgb import rgb_parser
from tsto2rgb.tools import (
    styles,
    generic_header,
    generic_body,
    generic_footer,
    write_str_to_file,
    report_progress,
)


def get_properties(directory, num, depth, time):
    definitions = Path(directory, "definitions.xml")

    # Set default values.
    offsetX = 0
    offsetY = 0
    properties = [[time, offsetX, offsetY, depth] for _ in range(num)]

    # Get current values.
    if definitions.exists() is True:
        tree = ET.parse(definitions)
        root = tree.getroot()

        for image, i in zip(root.findall("Image"), range(num)):
            time = float(image.attrib.get("time", time))
            offsetX = int(image.attrib.get("offsetX", offsetX))
            offsetY = int(image.attrib.get("offsetY", offsetY))
            depth = int(image.attrib.get("depth", depth))

            properties[i] = [time, offsetX, offsetY, depth]
    else:
        root = ET.Element("Definitions")
        for i in range(num):
            ET.SubElement(
                root,
                "Image",
                {
                    "time": str(properties[i][0]),
                    "offsetX": str(properties[i][1]),
                    "offsetY": str(properties[i][2]),
                    "depth": str(properties[i][3]),
                },
            )
        tree = ET.ElementTree(root)
        ET.indent(tree, "  ")
        with open(definitions, "wb") as xml_file:
            tree.write(xml_file)

    return properties


def bcell_parser(img_list, target):
    # Write bcell file and convert images to rgb.
    with open(target, "wb") as f:
        # Write bcell header.
        f.write("bcell13".encode())

        # Write some flag.
        f.write(b"\x01")

        # Number of images.
        f.write(len(img_list).to_bytes(2, "little"))

        for img, time, x, y in img_list:
            write_str_to_file(
                f, img.parent.name + f"_{img.stem}.rgb", null_terminated=True
            )

            # Write time in miliseconds.
            f.write(np.array(time, dtype=np.float32).tobytes())

            # X and Y.
            f.write(int.to_bytes(x, 2, "little", signed=True))
            f.write(int.to_bytes(y, 2, "little", signed=True))

            # Additional images.
            f.write(int.to_bytes(1, 2))
            write_str_to_file(f, "null", null_terminated=True)
            write_str_to_file(f, "null", null_terminated=True)

            ## Position, transformation and possibly alpha.
            f.write(np.array([0, 0, 1, 0, 0, 1, 1], dtype=np.float32).tobytes())

        return (True, "")


def bcell_gen(directories, target, total, input_extension, depth, time):
    generic_header(styles["bcell"], "bcell", total, input_extension, depth)
    generic_body(styles["bcell"])

    invalid_directories = []
    for i in range(total):
        img_list = natsorted(directories[i].glob(f"*.{input_extension}"))
        img_filter = list()

        # Try to convert these images to rgb.
        for img, item in zip(
            img_list, get_properties(directories[i], len(img_list), depth, time)
        ):
            with Image(filename=img) as main_img:
                width = main_img.width + (main_img.width % 2 > 0)
                height = main_img.height + (main_img.height % 2 > 0)
                time, offsetX, offsetY, img_depth = item

                with Image(width=width, height=height) as new_img:
                    new_img.composite(main_img, 0, 0)

                    x = -new_img.width // 2 + offsetX
                    y = -new_img.height + offsetY
                    status = rgb_parser(
                        new_img,
                        Path(target, directories[i].name + f"_{img.stem}.rgb"),
                        img_depth,
                    )

            if status is False:
                invalid_directories.append(
                    img.relative_to(img.parent).name + ": was not converted!"
                )
            else:
                img_filter.append((img, time, x, y))

        status, reason = bcell_parser(
            img_filter,
            Path(target, directories[i].name + ".bcell"),
        )
        report_progress(
            f" * Progress: {(i + 1) * 100 // total:3d}% -> {directories[i].name}.bcell",
            "",
            styles["normal"],
        )
        if status is False:
            invalid_directories.append(directories[i].name + f": {reason}")

    generic_footer(styles["bcell"], total, invalid_directories)
