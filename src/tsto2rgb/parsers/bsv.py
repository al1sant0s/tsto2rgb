import json
import os
import subprocess
import tempfile
import numpy as np
import xml.etree.ElementTree as ET
from natsort import natsorted
from wand.image import Image
from pathlib import Path
from tsto2rgb.parsers import rgb_parser
from tsto2rgb.tools import (
    styles,
    generic_header,
    generic_body,
    generic_footer,
    write_str_to_file,
    report_progress,
)

dicer = Path(Path(__file__).parent, "dicer", "linux")


def get_properties(directory, depth=4, alpha=255):
    definitions = Path(directory, "definitions.xml")

    # Get current values.
    offsetX = 0
    offsetZ = 0
    if definitions.exists() is True:
        tree = ET.parse(definitions)
        root = tree.getroot()

        offsetX = float(root.attrib.get("offsetX", offsetX))
        offsetZ = float(root.attrib.get("offsetZ", offsetZ))
        depth = int(root.attrib.get("depth", depth))
        alpha = int(root.attrib.get("alpha", alpha))

    # Rewrite file to include any missing attributes.
    root = ET.Element(
        "Definitions",
        {
            "offsetX": str(offsetX),
            "offsetZ": str(offsetZ),
            "depth": str(depth),
            "alpha": str(alpha),
        },
    )
    tree = ET.ElementTree(root)
    ET.indent(tree, "  ")
    with open(definitions, "wb") as xml_file:
        tree.write(xml_file)

    return (offsetX, offsetZ, depth, alpha)


def dicer_parser(atlas_width, atlas_height, sprites, offsetX, offsetZ):
    with open(sprites, "r") as f:
        # Reorganize frames.
        data = json.load(f)

        # Reoder with a dictonary.
        data_dict = {item["id"]: item for item in data}
        data_reorder = natsorted(anim for anim in data_dict.keys())

        # List of cells, frames and animations.
        cells_set = set()
        cells_list = list()
        frames = list()
        animations = dict()

        for state, index in zip(data_reorder, range(len(data_reorder))):
            frame = data_dict[state]
            animations[frame["id"].rsplit(os.sep, maxsplit=1)[0]] = index
            blocks = list()

            # Crop regions.
            vertices = frame["vertices"]
            uvs = frame["uvs"]
            indices = frame["indices"]

            for i in range(0, len(indices), 6):
                block = list()
                cos = np.cos(27.5 * np.pi / 180)
                sin = np.sin(27.5 * np.pi / 180)
                matrix = np.array([[cos, sin], [-cos, sin]]).transpose()
                offsets = np.array([offsetX, offsetZ])
                pos = (
                    np.array([vertices[indices[i]]["x"], vertices[indices[i]]["y"]])
                    + np.matmul(
                        matrix,
                        np.array(
                            [-frame["rect"]["width"] / 2, -frame["rect"]["height"] / 2]
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
                cells_set.add(cell)
                if len(cells_list) < len(cells_set):
                    cells_list.append(cell)

                # Add all info to the frame block.
                block.append(cells_list.index(cell))
                block.append(pos[0])
                block.append(pos[1])

                blocks.append(block)

            frames.append(blocks)
        return (frames, cells_list, animations)


def bsv3_259(target, frames, cells, animations, alpha=255):
    with open(target, "wb") as f:
        # Write file signature.
        f.write(b"\x03\x01")

        # Write cellnumber.
        f.write(len(cells).to_bytes(2, "little"))

        # Alpha flag.
        alpha_flag = alpha < 255
        f.write(alpha_flag.to_bytes())

        # Write cellnames and positions.
        for i in range(len(cells)):
            cellname = f"C_cell_{i:02d}"
            cell = cells[i]
            x, y, w, h = cell

            write_str_to_file(f, cellname, null_terminated=True)

            f.write(x.to_bytes(2, "little"))
            f.write(y.to_bytes(2, "little"))
            f.write(w.to_bytes(2, "little"))
            f.write(h.to_bytes(2, "little"))

        # Write frame data.
        f.write(len(frames).to_bytes(2, "little"))

        for frame in frames:
            # Block number.
            f.write(len(frame).to_bytes(2, "little"))

            # Null byte.
            f.write(b"\x00")

            for block in frame:
                index, x, y = block

                pos_trans = np.array([x, y, 1, 0, 0, 1], dtype=np.float32)

                f.write(index.to_bytes(2, "little"))
                f.write(pos_trans.tobytes())
                if alpha_flag is True:
                    f.write(int.to_bytes(alpha))

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


#                    with atlas_img.clone() as clone:
#                        clone.crop(u1, v1, width=u2 - u1, height=v2 - v1)
#                        img.composite(clone, x, y)


def bsv_parser(directory, target, offsetX, offsetZ, depth, alpha):
    # First check if there are subdirectories there.
    subdirectories = [
        subdirectory
        for subdirectory in directory.iterdir()
        if subdirectory.is_dir() is True
    ]
    if len(subdirectories) > 0:
        with tempfile.TemporaryDirectory() as tempdir:
            dicer_args = [
                dicer,
                "--square",
                "-l",
                "2048",
                "-o",
                tempdir,
                "-r",
            ]
            # Call dicer.
            status = subprocess.run(
                dicer_args + [directory],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            ).returncode
            if status == 0:
                jsonfile = Path(tempdir, "sprites.json")
                atlases = list(Path(tempdir).glob("*.png"))
                if jsonfile.exists() is False:
                    return (False, "sprites.json not created!")
                elif len(atlases) == 0:
                    return (False, "no atlas found!")
                elif len(atlases) > 1:
                    return (False, "too many atlases created!")
                else:
                    atlas = Path(tempdir, "atlas_0.png")
                    sprites = Path(tempdir, "sprites.json")

                    # Open atlas and rescale image if necessary.
                    with Image(filename=atlas) as atlas_img:
                        atlas_width = atlas_img.width
                        atlas_height = atlas_img.height

                        frames, cells, animations = dicer_parser(
                            atlas_width,
                            atlas_height,
                            sprites,
                            offsetX,
                            offsetZ,
                        )
                        if (
                            rgb_parser(
                                atlas_img, Path(target, directory.name + ".rgb"), depth
                            )
                            is False
                        ):
                            return (False, "atlas conversion to rgb failed!")
                        bsv3_259(
                            Path(target, directory.name + ".bsv3"),
                            frames,
                            cells,
                            animations,
                            alpha,
                        )

                        # Required in game xml file.
                        building = Path(target, directory.name + ".xml")
                        if building.exists() is False:
                            root = ET.Element(
                                "Building",
                                attrib={
                                    "x": "5",
                                    "z": "5",
                                    "height": "3.5",
                                    "locX": "1",
                                    "locY": "5",
                                    "transImageX": "0.0",
                                    "transImageY": "0.0",
                                },
                            )
                            tree = ET.ElementTree(root)
                            ET.indent(tree, "  ")
                            with open(building, "wb") as xml_file:
                                tree.write(xml_file)

                    return (True, "")
            else:
                return (False, "Dicer failed!")
    else:
        return (False, "No animation subdirectories found!")


def bsv_gen(directories, target, total, input_extension, depth, alpha):
    generic_header(styles["bsv"], "bsv", total, input_extension, depth)
    generic_body(styles["bsv"])
    invalid_directories = []
    for i in range(total):
        report_progress(
            f" * Progress: {(i + 1) * 100 // total:3d}% -> {directories[i].stem}.bsv3",
            "",
            styles["normal"],
        )
        offsetX, offsetZ, depth, alpha = get_properties(directories[i], depth, alpha)
        status, reason = bsv_parser(
            directories[i], target, offsetX, offsetZ, depth, alpha
        )
        if status is False:
            invalid_directories.append(directories[i].name + f": {reason}")

    generic_footer(styles["bsv"], total, invalid_directories)
