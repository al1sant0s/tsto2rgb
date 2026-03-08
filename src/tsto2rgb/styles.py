from colorama import Style, Fore

divlen = 62

# Formatting styles.
styles = {
    "rgb": Fore.LIGHTMAGENTA_EX,
    "bsv": Fore.LIGHTGREEN_EX,
    "bcell": Fore.LIGHTYELLOW_EX,
    "normal": Style.DIM + Fore.WHITE,
    "error": Style.BRIGHT + Fore.RED,
    "noerror": Style.BRIGHT + Fore.GREEN
}

def colorprint(style, message, end="\n"):
    print(style + message, end=end)
    print(Style.RESET_ALL, end=end)


def generic_div_str(divchar, divlen, name):
    charlen = (divlen - len(name))//2
    return divchar * charlen + " " + name + " " + divchar * charlen

def generic_header(style, name, total, extension, depth):

    header_str = generic_div_str("=", divlen, f"{name.upper()} GENERATOR")
    colorprint(style,
        f"\n\n{header_str}\n\n",
        end=""
    )
    colorprint(style, f" * Operation: {extension.upper()} => {name.upper()}")
    colorprint(style, f" * Files: {total}")
    colorprint(style, f" * Depth: {depth}")


def generic_body(style):
    body_str = generic_div_str(".", divlen, "WORKING")
    colorprint(style,
        f"\n{body_str}\n\n",
        end=""
    )

def generic_footer(style, total, error_files):
    footer_str = generic_div_str(".", divlen, "RESULTS")

    colorprint(style,
        f"\n\n{footer_str}\n\n",
        end=""
    )
    errors = len(error_files)
    alt_style = styles["noerror"] if errors == 0 else styles["error"]
    colorprint(alt_style, f" * Errors: {errors}")

    if errors > 0:
        for i in range(len(error_files)):
            colorprint(styles["error"] + Style.DIM, f" {i+1}) {error_files[i]}")

    #colorprint(style,
    #    "\n\n" + (divlen + 2) * "=",
    #    end=""
    #)

