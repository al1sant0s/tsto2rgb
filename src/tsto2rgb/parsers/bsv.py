import platform
import json
import os
import shutil
import subprocess
import tempfile
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


def get_dicer_path():
    os_name = platform.system().lower()
    dicer = Path(Path(__file__).parent, "dicer").glob(f"*{os_name}*")

    return next(dicer)


def set_properties(directory, depth=4, alpha=1.0):
    building_definitions = Path(directory, directory.name.lower() + ".xml")

    # Get default values.
    defaults = {
        "x": "7",
        "z": "5",
        "height": "3.5",
        "locX": "3",
        "locY": "1",
        "transImageX": "0.0",
        "transImageY": "0.0",
        "offsetX": "0",
        "offsetZ": "0",
        "depth": str(depth),
        "alpha": str(alpha)
    }

    # Read existing file to update default attribute values and include missing attributes.
    if building_definitions.exists() is True:
        tree = ET.parse(building_definitions)
        root = tree.getroot()

        for key, value in defaults.items():
            defaults[key] = root.get(key, value)


    root = ET.Element("Building", defaults)
    tree = ET.ElementTree(root)
    ET.indent(tree, "  ")
    with open(building_definitions, "wb") as xml_file:
        tree.write(xml_file)


    return building_definitions


def dicer_parser(atlases_widths, atlases_heights, data, offsetX, offsetZ):

    # Organize frames with a dictonary.
    data_dict = {item["id"]: item for item in data}
    data_reorder = natsorted(anim for anim in data_dict.keys())

    # List of ids, frames, cells and animations.
    atlases_index = list()
    frames = list()
    cells_set = [set() for _ in range(len(atlases_widths))]
    cells_list = [list() for _ in range(len(atlases_widths))]
    animations = dict()

    for state, index in zip(data_reorder, range(len(data_reorder))):
        frame = data_dict[state]
        animations[frame["id"].rsplit(os.sep, maxsplit=1)[0]] = index
        blocks = list()

        # Crop regions.
        vertices = frame["vertices"]
        uvs = frame["uvs"]
        indices = frame["indices"]
        atlas_index = frame["atlas"]
        atlas_width = atlases_widths[atlas_index]
        atlas_height = atlases_heights[atlas_index]

        for i in range(0, len(indices), 6):
            block = list()
            cos = np.cos(27.5 * np.pi / 180)
            sin = np.sin(27.5 * np.pi / 180)
            matrix = np.array([[cos, -sin], [-cos, -sin]]).transpose()
            offsets = np.array([offsetX, offsetZ])
            pos = (
                np.array([vertices[indices[i]]["x"], vertices[indices[i]]["y"]])
                + np.matmul(
                    matrix,
                    np.array(
                        [frame["rect"]["width"]/2, frame["rect"]["height"]/2]
                    )
                    + offsets,
                )
            ) * 100

            # x = vertices[indices[i]]["x"] * 100 + frame["rect"]["width"] * 100
            # y = vertices[indices[i]]["y"] * 100 - frame["rect"]["height"] * 0
            u1 = round(uvs[indices[i]]["u"] * atlas_width)
            v1 = round(uvs[indices[i]]["v"] * atlas_height)
            u2 = round(uvs[indices[i + 2]]["u"] * atlas_width)
            v2 = round(uvs[indices[i + 2]]["v"] * atlas_height)

            # Add cell only if new.
            cell = (u1, v1, u2 - u1, v2 - v1)
            cells_set[atlas_index].add(cell)
            if len(cells_list[atlas_index]) < len(cells_set[atlas_index]):
                cells_list[atlas_index].append(cell)

            # Add all info to the frame block.
            block.append(cells_list[atlas_index].index(cell))
            block.append(pos[0])
            block.append(pos[1])

            blocks.append(block)


        atlases_index.append(frame["atlas"])
        frames.append(blocks)


    return (atlases_index, frames, cells_list, animations)


def bsv3_259(bsv_files, atlases_index, frames, cells, animations, alpha=1.0):


    for i in range(len(bsv_files)):

        target = bsv_files[i]

        with open(target, "wb") as f:
            # Write file signature.
            f.write(b"\x03\x01")

            # Write cellnumber.
            f.write(len(cells[i]).to_bytes(2, "little"))

            # Alpha flag.
            alpha = int(alpha * 255)
            alpha_flag = alpha < 255
            f.write(alpha_flag.to_bytes())

            # Write cellnames and positions.
            for j in range(len(cells[i])):
                cellname = f"C_{target.stem}_Crop_{j:02d}"
                cell = cells[i][j]
                x, y, w, h = cell

                write_str_to_file(f, cellname, null_terminated=True)

                f.write(x.to_bytes(2, "little"))
                f.write(y.to_bytes(2, "little"))
                f.write(w.to_bytes(2, "little"))
                f.write(h.to_bytes(2, "little"))

            # Write frame data.
            f.write(len(frames).to_bytes(2, "little"))

            for frame, atlas_id in zip(frames, atlases_index):

                # Block number.
                if i == atlas_id:
                    f.write(len(frame).to_bytes(2, "little"))

                    # Null byte.
                    f.write(b"\x00")

                    for block in frame:
                        index, x, y = block

                        if index > len(cells[i]):
                            continue

                        pos_trans = np.array([x, y, 1, 0, 0, 1], dtype=np.float32)

                        f.write(index.to_bytes(2, "little"))
                        f.write(pos_trans.tobytes())
                        if alpha_flag is True:
                            f.write(int.to_bytes(alpha))

                else:
                    f.write(int.to_bytes(0, 3, "little"))


            # Write animations.
            f.write(len(animations).to_bytes(2, "little"))

            last_index = 0
            for name, index in zip(animations.keys(), animations.values()):
                # Animation name.
                write_str_to_file(f, name, null_terminated=True)

                # First frame.
                f.write(last_index.to_bytes(2, "little"))

                # Last frame.
                f.write(index.to_bytes(2, "little"))
                last_index = index + 1



def bsv_parser(dicer_path, directory, building_definitions, target):
    # First check if there are subdirectories there.
    subdirectories = [
        subdirectory
        for subdirectory in directory.iterdir()
        if subdirectory.is_dir() is True
    ]
    if len(subdirectories) > 0:


        # Load building definitions.
        root = ET.parse(building_definitions).getroot()
        offsetX = float(root.get("offsetX"))    # type: ignore
        offsetZ = float(root.get("offsetZ"))    # type: ignore
        depth = int(root.get("depth"))          # type: ignore
        alpha = float(root.get("alpha"))        # type: ignore


        for scale in (25, 50, 100):
            with tempfile.TemporaryDirectory() as tempdir:

                # Copy images to tempdir for rescaling them.
                temp_source = Path(tempdir, directory.name)
                temp_source.mkdir(exist_ok = True)
                for animation in subdirectories:
                    shutil.copytree(animation, Path(temp_source, animation.name))


                for animation in temp_source.iterdir():
                    images = natsorted(animation.glob("*.png"))
                    for i in range(len(images)):
                        with Image(filename = images[i]) as img:
                            img.transform(resize = f"{scale}%")
                            img.save(filename = Path(animation, f"{i}.png"))
                        shutil.move(images[i], Path(animation, f"{i}.png"))


                dicer_args = [
                    dicer_path,
                    "--square",
                    "-l",
                    "2048",
                    "-o",
                    tempdir,
                    "-r",
                ]
                # Call dicer.
                status = subprocess.run(
                    dicer_args + [temp_source],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                ).returncode
                if status == 0:
                    jsonfile = Path(tempdir, "sprites.json")
                    atlases = natsorted(list(Path(tempdir).glob("*.png")))
                    atlases_number = len(atlases)
                    if jsonfile.exists() is False:
                        return (False, "sprites.json not created!")
                    elif atlases_number == 0:
                        return (False, "no atlas found!")
                    else:
                        subtarget = Path(target, target.name.split("_")[-1] + f"BuildDecoGame-{scale}")
                        subtarget.mkdir(exist_ok = True)
                        neutral_atlas_index = 0
                        atlases_widths = list()
                        atlases_heights = list()
                        data = dict()

                        # Load json file.
                        with open(jsonfile, "r") as jsonf:
                            data = json.load(jsonf)

                            # Attempt to find the 0 Neutral frame and make this atlas the main file (a file with a index number at the end).
                            for item in data:
                                if "neutral/0" in item.get("id", "").lower():
                                    neutral_atlas_index = item["atlas"]




                        # Put the atlas with the netraul frame at the begging of list so it becomes the main file.
                        rgb_files = [Path(subtarget, directory.name.lower() + ".rgb")] + [Path(subtarget, directory.name.lower() + f"_{index + 1}" + ".rgb") for index in range(atlases_number - 1)]
                        rgb_files[0], rgb_files[neutral_atlas_index] = rgb_files[neutral_atlas_index], rgb_files[0]
                        bsv_files = [Path(subtarget, rgb_file.stem + ".bsv3") for rgb_file in rgb_files]

                        # Open atlases, get dimensions, rescale images if necessary and convert them to rgb.
                        for i in range(atlases_number):
                            atlas = atlases[i]
                            with Image(filename=atlas) as atlas_img:
                                atlases_widths.append(atlas_img.width)
                                atlases_heights.append(atlas_img.height)

                                if (
                                    rgb_parser(
                                        atlas_img, rgb_files[i], depth
                                    )
                                    is False
                                ):
                                    return (False, "atlas conversion to rgb failed!")


                        atlases_index, frames, cells, animations = dicer_parser(
                            atlases_widths,
                            atlases_heights,
                            data,
                            offsetX * scale / 100,
                            offsetZ * scale / 100,
                        )

                        bsv3_259(
                            bsv_files,
                            atlases_index,
                            frames,
                            cells,
                            animations,
                            alpha,
                        )

                        tree = ET.ElementTree(ET.Element("Building", root.attrib))
                        ET.indent(tree, "  ")
                        with open(Path(subtarget, directory.name.lower() + ".xml"), "wb") as xml_file:
                            tree.write(xml_file)


                else:
                    return (False, "Dicer failed!")


        # Get additional images for the menus.
        menu_img = Path(directory, "menu.png")
        if menu_img.exists() is True:
            with Image(filename = menu_img) as icon_img:
                make_icons(icon_img, target, "BuildDeco", directory.name.lower() + "_menu.rgb")


        return (True, "")

    else:
        return (False, "No animation subdirectories found!")


def bsv_gen(directories, target, total, input_extension, depth, alpha):
    generic_header(styles["bsv"], "bsv", total, input_extension, depth)
    generic_body(styles["bsv"])
    invalid_directories = []
    for i in range(total):
        report_progress(
            f" * Progress: {(i + 1) * 100 // total:3d}% -> {directories[i].stem.lower()}.bsv3",
            "",
            styles["normal"],
        )
        building_definitions = set_properties(directories[i], depth, alpha)
        status, reason = bsv_parser(
            get_dicer_path(), directories[i], building_definitions, target
        )
        if status is False:
            invalid_directories.append(directories[i].name + f": {reason}")

    generic_footer(styles["bsv"], total, invalid_directories)
