from tsto2rgb.tools import colorprint


def write_str_to_file(file_descriptor, str_name, bytelen=1, null_terminated=False):
    # String length.
    str_name = str_name.encode("utf8")
    strlen = len(str_name) + null_terminated
    file_descriptor.write(strlen.to_bytes(bytelen))

    # String.
    file_descriptor.write(str_name)

    if null_terminated is True:
        file_descriptor.write(b"\x00")


def report_progress(prefix_str, parsing_info, style):
    # Clear line.
    # colorprint(style, 150 * " ", end="\r")
    print(150 * " ", end="\r")

    # Print progress.
    colorprint(style, f"{prefix_str} {parsing_info}", end="\r")
