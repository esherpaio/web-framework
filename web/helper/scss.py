import sass


def compile_scss(src: str, out: str) -> None:
    """Compile SCSS to CSS."""

    scss = sass.compile(filename=src, output_style="compressed")
    with open(out, "w") as file:
        file.write(scss)
