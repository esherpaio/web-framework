import re


def markdown_to_html(text: str) -> str:
    # Regex pattern to match version headers and list items
    version_pattern = (
        r"## (v\d+\.\d+\.\d+ \(\d{4}-\d{2}-\d{2}\))"  # Matches version headers
    )
    item_pattern = r"^( *)(- .*)"  # Matches items with spaces for indentation

    # Split the markdown into sections by version headers
    sections = re.split(version_pattern, text)

    # Build the HTML output
    final_html = ""

    # Iterate over sections, skipping the first element as it will be empty
    for i in range(1, len(sections), 2):
        version_header = sections[i]
        content = sections[i + 1]

        # Create the main div and header
        div = f'<div class="col-12">\n    <h3>{version_header}</h3>\n    <ul>'

        # Split the content by line and process each line
        lines = content.split("\n")
        current_indent = 0
        sublist_stack = []

        for line in lines:
            match = re.match(item_pattern, line)
            if match:
                indent_level = len(match.group(1)) // 2
                item_text = match.group(2)[2:].strip()

                if indent_level > current_indent:
                    div += "\n        <ul>"
                    sublist_stack.append("</ul>")
                elif indent_level < current_indent:
                    while current_indent > indent_level:
                        div += f"\n        {sublist_stack.pop()}"
                        current_indent -= 1

                div += f"\n        <li>{item_text}</li>"
                current_indent = indent_level

        # Close any remaining open sublists
        while sublist_stack:
            div += f"\n        {sublist_stack.pop()}"

        div += "\n    </ul>\n</div>"
        final_html += div

    return final_html


if __name__ == "__main__":
    in_fp = "/home/stan/code/web-framework/RELEASE.md"
    out_fp = "/home/stan/code/web-framework/web/app/blueprint/admin_v1/templates/admin/_changelog.html"
    with open(in_fp, "r") as f:
        text = "".join(f.readlines())
    html = markdown_to_html(text)
    with open(out_fp, "w") as f:
        f.write(html)
