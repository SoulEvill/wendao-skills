"""Check discovery metadata and self-contained local links in installable skills."""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def check_links(document, boundary):
    errors = []
    for raw in LINK.findall(document.read_text()):
        target = urlsplit(raw.strip("<>"))
        if target.scheme or target.netloc or not target.path:
            continue
        path = (document.parent / unquote(target.path)).resolve()
        if not path.is_relative_to(boundary.resolve()):
            errors.append(f"{document.relative_to(ROOT)}: link escapes package: {raw}")
        elif not path.exists():
            errors.append(f"{document.relative_to(ROOT)}: missing linked file: {raw}")
    return errors


def check_skill(directory):
    errors = []
    entrypoint = directory / "SKILL.md"
    text = entrypoint.read_text()
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not frontmatter:
        return [f"{entrypoint.relative_to(ROOT)}: missing YAML frontmatter"]
    try:
        metadata = yaml.safe_load(frontmatter.group(1))
    except yaml.YAMLError as exc:
        return [f"{entrypoint.relative_to(ROOT)}: invalid YAML: {exc}"]
    if not isinstance(metadata, dict):
        return [f"{entrypoint.relative_to(ROOT)}: frontmatter must be a mapping"]
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
        errors.append(f"{directory.name}: invalid skill name")
    if name != directory.name:
        errors.append(f"{directory.name}: name must match its folder")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append(f"{directory.name}: description must contain 1 to 1024 characters")
    for path in directory.rglob("*"):
        if path.is_symlink() and not path.resolve().is_relative_to(directory.resolve()):
            errors.append(f"{path.relative_to(ROOT)}: symlink escapes skill")
        if path.is_file() and path.suffix == ".md":
            errors.extend(check_links(path, directory))
    interface = directory / "agents" / "openai.yaml"
    if interface.exists():
        try:
            value = yaml.safe_load(interface.read_text())
            if not isinstance(value, dict):
                errors.append(f"{interface.relative_to(ROOT)}: metadata must be a mapping")
        except yaml.YAMLError as exc:
            errors.append(f"{interface.relative_to(ROOT)}: invalid YAML: {exc}")
    return errors


def main():
    directories = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    errors = []
    if not directories:
        errors.append("No skill folders found")
    for directory in directories:
        if not (directory / "SKILL.md").is_file():
            errors.append(f"{directory.relative_to(ROOT)}: missing SKILL.md")
        else:
            errors.extend(check_skill(directory))
    for document in [ROOT / "README.md", ROOT / "CONTRIBUTING.md",
                     ROOT / "tests" / "README.md"]:
        errors.extend(check_links(document, ROOT))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(directories)} skill package(s) and repository documentation links.")


if __name__ == "__main__":
    main()
