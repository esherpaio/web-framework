import sass

#
# Functions
#


def compile_scss(src: str, out: str) -> None:
    """Compile SCSS to CSS."""
    scss = sass.compile(filename=src, output_style="compressed")
    with open(out, "w") as file_:
        file_.write(scss)
