#!/usr/bin/env python3
"""Build the documentation site into site/ (MkDocs Material). The README becomes the home page."""
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "build" / "docs"
# Root files and where they live in the site.
ROOT_PAGES = {"README.md": "index.md", "CHANGELOG.md": "changelog.md", "THIRD-PARTY-NOTICES.md": "third-party-notices.md", "LICENSE": "license.md"}
# README sections about building Ferry from source, which is not public.
PRIVATE_SECTIONS = ("Build and test",)


def relink(text, depth):
    """Point links at the site's pages: docs/x.md -> x.md, LICENSE -> license.md, and so on."""
    up = "../" * depth
    def fix(match):
        label, target = match.groups()
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            return match.group(0)
        file, _, anchor = target.partition("#")
        name = pathlib.PurePosixPath(file).name
        if name in ROOT_PAGES:
            file = up + ROOT_PAGES[name]
        elif file.startswith("docs/"):
            file = file[len("docs/"):]
        return f"[{label}]({file}{'#' + anchor if anchor else ''})"
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", fix, text)


def without_sections(text, titles):
    for title in titles:
        text = re.sub(rf"^## {re.escape(title)}\n.*?(?=^## |\Z)", "", text, flags=re.S | re.M)
    return text


def main():
    shutil.rmtree(ROOT / "build", ignore_errors=True)
    shutil.copytree(ROOT / "docs", BUILD)
    for path in BUILD.rglob("*.md"):
        path.write_text(relink(path.read_text(encoding="utf-8"), len(path.relative_to(BUILD).parts) - 1), encoding="utf-8")
    for source, page in ROOT_PAGES.items():
        text = (ROOT / source).read_text(encoding="utf-8")
        if source == "LICENSE":
            text = "# License\n\n```text\n" + text + "\n```\n"
        if source == "README.md":
            text = without_sections(text, PRIVATE_SECTIONS)
        (BUILD / page).write_text(relink(text, 0), encoding="utf-8")
    mkdocs = pathlib.Path(sys.executable).parent / "mkdocs"
    subprocess.run([str(mkdocs), "build", "--strict", "--clean"], cwd=ROOT, check=True)
    (ROOT / "site" / ".nojekyll").touch()
    print(f"Site built in {ROOT / 'site'}")


if __name__ == "__main__":
    main()
