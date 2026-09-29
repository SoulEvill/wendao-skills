"""Validate the catalog and list its self-contained installable skills."""

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
import yaml


ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"wd-[a-z0-9]+(?:-[a-z0-9]+)*")
MARKDOWN = MarkdownIt("commonmark")


def label(path):
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def discover_skills(skills_root):
    """Accept flat skills or one group level, with unique leaf names."""
    if not skills_root.is_dir():
        raise ValueError(f"{label(skills_root)}: no skill folders found")
    directories = []
    errors = []
    if (skills_root / "SKILL.md").exists():
        errors.append(f"{label(skills_root)}: the catalog root cannot be a skill")

    def add_skill(directory):
        directories.append(directory)
        for nested in sorted(directory.rglob("SKILL.md")):
            if nested != directory / "SKILL.md":
                errors.append(f"{label(nested)}: a skill cannot contain another skill")

    for directory in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        if not directory.resolve().is_relative_to(skills_root.resolve()):
            errors.append(f"{label(directory)}: folder escapes catalog")
            continue
        if (directory / "SKILL.md").is_file():
            add_skill(directory)
            continue
        children = sorted(path for path in directory.iterdir() if path.is_dir())
        if not children:
            errors.append(f"{label(directory)}: missing SKILL.md or grouped skills")
        for child in children:
            if not child.resolve().is_relative_to(skills_root.resolve()):
                errors.append(f"{label(child)}: folder escapes catalog")
            elif not (child / "SKILL.md").is_file():
                errors.append(
                    f"{label(child)}: expected SKILL.md; only one group level is supported"
                )
            else:
                add_skill(child)

    names = set()
    for directory in directories:
        if directory.name in names:
            errors.append(f"{label(directory)}: duplicate skill name: {directory.name}")
        names.add(directory.name)
    if not directories:
        errors.append("No skill folders found")
    if errors:
        raise ValueError("\n".join(errors))
    return sorted(directories)


def check_links(document, boundary):
    """Check real Markdown links and images, excluding literal code examples."""
    errors = []
    for block in MARKDOWN.parse(document.read_text()):
        for token in block.children or []:
            if token.type not in {"link_open", "image"}:
                continue
            raw = token.attrGet("href" if token.type == "link_open" else "src")
            try:
                target = urlsplit(raw)
            except ValueError:
                errors.append(f"{label(document)}: invalid link target: {raw}")
                continue
            if target.scheme or target.netloc or not target.path:
                continue
            path = (document.parent / unquote(target.path)).resolve()
            if not path.is_relative_to(boundary.resolve()):
                errors.append(f"{label(document)}: link escapes package: {raw}")
            elif not path.exists():
                errors.append(f"{label(document)}: missing linked file: {raw}")
    return errors


def check_skill(directory):
    errors = []
    entrypoint = directory / "SKILL.md"
    if not (directory / "README.md").is_file():
        errors.append(f"{label(directory)}: missing README.md")
    if not entrypoint.is_file():
        return errors + [f"{label(directory)}: missing SKILL.md"]
    text = entrypoint.read_text()
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not frontmatter:
        return errors + [f"{label(entrypoint)}: missing YAML frontmatter"]
    try:
        metadata = yaml.safe_load(frontmatter.group(1))
    except yaml.YAMLError as exc:
        return errors + [f"{label(entrypoint)}: invalid YAML: {exc}"]
    if not isinstance(metadata, dict):
        return errors + [f"{label(entrypoint)}: frontmatter must be a mapping"]
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
        errors.append(
            f"{label(directory)}: skill name must use wd- followed by lowercase "
            "letters, digits, and single hyphens (64 characters maximum)"
        )
    if name != directory.name:
        errors.append(f"{label(directory)}: name must match its folder")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append(f"{label(directory)}: description must contain 1 to 1024 characters")
    for path in directory.rglob("*"):
        if path.is_symlink() and not path.resolve().is_relative_to(directory.resolve()):
            errors.append(f"{label(path)}: symlink escapes skill")
            continue
        if path.is_file() and path.suffix == ".md":
            errors.extend(check_links(path, directory))
    interface = directory / "agents" / "openai.yaml"
    if interface.exists() and interface.resolve().is_relative_to(directory.resolve()):
        try:
            value = yaml.safe_load(interface.read_text())
            if not isinstance(value, dict):
                errors.append(f"{label(interface)}: metadata must be a mapping")
        except yaml.YAMLError as exc:
            errors.append(f"{label(interface)}: invalid YAML: {exc}")
    return errors


def validate_package(root):
    try:
        directories = discover_skills(root / "skills")
    except ValueError as exc:
        return [], [str(exc)]
    errors = []
    for directory in directories:
        errors.extend(check_skill(directory))
    documents = [root / "README.md", root / "CONTRIBUTING.md", root / "AGENTS.md",
                 root / "tests" / "README.md", *sorted((root / "docs").glob("*.md"))]
    for document in documents:
        if document.is_file():
            errors.extend(check_links(document, root))
    return directories, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Catalog root (defaults to this checkout)")
    parser.add_argument("--list", action="store_true", help="Validate, then print skill names and source folders as TSV")
    arguments = parser.parse_args()
    directories, errors = validate_package(arguments.root.resolve())
    if errors:
        raise SystemExit("\n".join(errors))
    if arguments.list:
        for directory in directories:
            print(f"{directory.name}\t{directory}")
    else:
        print(f"Validated {len(directories)} skill package(s) and repository documentation links.")


if __name__ == "__main__":
    main()
