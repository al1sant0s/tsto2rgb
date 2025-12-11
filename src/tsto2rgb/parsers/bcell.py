import numpy as np
import xml.etree.ElementTree as ET
from natsort import natsorted
from wand.image import Image
from pathlib import Path
from tsto2rgb.parsers.rgb import rgb_parser, make_icons
from tsto2rgb.tools import (
    styles,
    generic_header,
    generic_body,
    generic_footer,
    write_str_to_file,
    report_progress,
)


def set_properties(directory, num, delay, depth):
    cell_definitions = Path(directory, directory.parent.name + "_" + directory.name.lower() + ".xml")

    # Get default values.

    root_defaults = {
        "offsetX": "0",
        "offsetY": "0",
        "depth": str(depth),
    }

    cell_defaults = {
        "delay": str(delay),
    }

    animseq = ET.Element("AnimSequence", root_defaults)
    cells = [ET.SubElement(animseq, "Cell", cell_defaults) for _ in range(num)]

    # Read existing file to update default attribute values and include missing attributes.
    if cell_definitions.exists() is True:
        root = ET.parse(cell_definitions).getroot()

        for key, value in root_defaults.items():
            root.attrib[key] = root.get(key, value)
        animseq.attrib = root.attrib

        for item, cell in zip(root.findall("*"), cells):
            for key, value in cell_defaults.items():
                item.attrib[key] = item.get(key, value)

            cell.attrib = item.attrib


    tree = ET.ElementTree(animseq)
    ET.indent(tree, "  ")
    with open(cell_definitions, "wb") as xml_file:
        tree.write(xml_file)


    return cell_definitions


def bcell_parser(img_list, target):
    # Write bcell file and convert images to rgb.
    with open(target, "wb") as f:
        # Write bcell header.
        f.write("bcell13".encode())

        # Write some flag.
        f.write(b"\x01")

        # Number of images.
        f.write(len(img_list).to_bytes(2, "little"))

        for img, delay, x, y in img_list:
            write_str_to_file(
                f, img.parent.parent.name + "_" + img.parent.name + f"_{img.stem}.rgb", null_terminated=True
            )

            # Write delay in miliseconds.
            f.write(np.array(delay, dtype=np.float32).tobytes())

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


def bcell_gen(directories, target, total, input_extension, depth, delay):
    generic_header(styles["bcell"], "bcell", total, input_extension, depth)
    generic_body(styles["bcell"])

    invalid_directories = []
    for directory in directories:

        subdirectories = [subdirectory for subdirectory in directory.iterdir() if subdirectory.is_dir() is True]
        subtotal = len(subdirectories)

        for scale in (25, 50, 100):

            # Create animation file.
            animlist = ET.Element("AnimList")

            subtarget = Path(target, target.name.split("_")[-1] + f"Game-{scale}")
            subtarget.mkdir(exist_ok = True)

            for i in range(subtotal):


                img_list = natsorted(subdirectories[i].glob(f"*.{input_extension}"))
                img_filter = list()

                cell_definitions = set_properties(subdirectories[i], len(img_list), delay, depth)
                root = ET.parse(cell_definitions).getroot()
                cells = [element for element in root.findall("*")]

                # Try to convert these images to rgb.
                for img, cell in zip(img_list, cells):
                    with Image(filename=img) as main_img:
                        main_img.transform(resize = f"{scale}%")
                        #width = main_img.width + (main_img.width % 2 > 0)
                        #height = main_img.height + (main_img.height % 2 > 0)

                        #with Image(width=width, height=height) as new_img:
                        #    new_img.composite(main_img, 0, 0)

                        x = int(-main_img.width // 2 + int(root.attrib["offsetX"]) * scale / 100)
                        y = int(-main_img.height + int(root.attrib["offsetY"]) * scale / 100)
                        status = rgb_parser(
                            main_img,
                            Path(subtarget, directory.name.lower() + "_" + subdirectories[i].name.lower() + f"_{img.stem}.rgb"),
                            int(root.attrib["depth"]),
                        )

                    if status is False:
                        invalid_directories.append(
                            img.relative_to(img.parent.parent).name + ": was not converted!"
                        )
                    else:
                        img_filter.append((img, float(cell.attrib["delay"]), x, y))

                status, reason = bcell_parser(
                    img_filter,
                    Path(subtarget, directory.name.lower() + "_" + subdirectories[i].name.lower() + ".bcell"),
                )
                report_progress(
                    f" * Progress: {(i + 1) * 100 // subtotal:3d}% -> {directory.name.lower() + "_" + subdirectories[i].name.lower()}.bcell",
                    "",
                    styles["normal"],
                )
                if status is False:
                    invalid_directories.append(subdirectories[i].name + f": {reason}")
                else:
                    ET.SubElement(
                        animlist,
                        "Animation",
                        {
                            "name":
                            "_".join([s.capitalize() for s in subdirectories[i].name.split("_")])
                        }
                    )

                    tree = ET.ElementTree(animlist)
                    ET.indent(tree, "  ")
                    with open(Path(subtarget, directory.name.lower() + ".xml"), "wb") as xml_file:
                        tree.write(xml_file)


        # Get additional images for the menus.
        menu_img = Path(directory, "menu.png")
        if menu_img.exists() is True:
            with Image(filename = menu_img) as icon_img:
                make_icons(icon_img, target, directory.name.lower() + "_menu.rgb")


    generic_footer(styles["bcell"], total, invalid_directories)
