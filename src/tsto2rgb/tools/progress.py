from tsto2rgb.parsers.styles import colorprint

def report_progress(prefix_str, parsing_info, style):
    # Clear line.
    #colorprint(style, 150 * " ", end="\r")
    print(150 * " ", end="\r")

    # Print progress.
    colorprint(style, f"{prefix_str} {parsing_info}", end="\r")
