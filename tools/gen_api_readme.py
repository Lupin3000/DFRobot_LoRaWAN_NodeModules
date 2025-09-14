import ast
import re
import sys
import textwrap
from typing import List


def is_public(name: str) -> bool:
    return not name.startswith("_")


def clean_docstring(doc: str) -> str:
    if not doc:
        return ""

    lines = doc.splitlines()
    filtered = []

    for line in lines:
        if re.match(r"^\s*:", line):
            continue

        filtered.append(line)

    return "\n".join(filtered).strip()


def generate_markdown(source_path: str) -> str:
    with open(source_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=source_path)

    lines: List[str] = []

    lines.append("# API")
    lines.append("")

    classes: List[ast.ClassDef] = [
        n for n in tree.body if isinstance(n, ast.ClassDef) and is_public(n.name)
    ]

    for cls in classes:
        lines.append(f"## {cls.name}")
        lines.append("")

        methods = [
            n for n in cls.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(n.name)
        ]

        if methods:
            for m in methods:
                prefix = "async " if isinstance(m, ast.AsyncFunctionDef) else ""
                lines.append(f"### {prefix}{m.name}")
                lines.append("")
                raw_doc = ast.get_docstring(m) or "_No Description._"
                mdoc = clean_docstring(textwrap.dedent(raw_doc))
                lines.append(mdoc if mdoc else "_No Description._")
                lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python gen_api_readme.py <sourcefile.py> [<outfile.md>]")
        sys.exit(1)

    source_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "readme_api.md"

    md = generate_markdown(source_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"API-Document generated: {output_path}")


if __name__ == "__main__":
    main()
