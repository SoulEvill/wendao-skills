"""Exercise package discovery and Markdown boundaries without installing skills."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).resolve().parents[2] / "scripts" / "validate_package.py"
SPEC = importlib.util.spec_from_file_location("validate_package", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PackageValidatorTests(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory(prefix="wd-package-tests-")
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.skills = self.root / "skills"
        self.skills.mkdir()

    def write(self, path, text="content\n"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def skill(self, relative_path, *, name=None, readme=True):
        directory = self.skills / relative_path
        self.write(
            directory / "SKILL.md",
            f"---\nname: {name or directory.name}\ndescription: Review a bounded example.\n---\n"
            "# Example skill\n",
        )
        if readme:
            self.write(directory / "README.md", "# Usage\n")
        return directory

    def test_discovers_flat_and_grouped_skills_in_sorted_order(self):
        flat = self.skill("wd-zebra")
        grouped = self.skill("engineering/wd-review")
        other = self.skill("wd-alpha")

        self.assertEqual(
            validator.discover_skills(self.skills), sorted([flat, grouped, other])
        )

    def test_rejects_no_skills_and_empty_groups(self):
        with self.assertRaises(ValueError):
            validator.discover_skills(self.skills)

        self.skill("wd-valid")
        (self.skills / "empty-group").mkdir()
        with self.assertRaises(ValueError):
            validator.discover_skills(self.skills)

    def test_rejects_duplicate_install_names_across_layouts(self):
        cases = (
            ("wd-review", "engineering/wd-review"),
            ("engineering/wd-review", "operations/wd-review"),
        )
        for index, paths in enumerate(cases):
            with self.subTest(paths=paths):
                self.skills = self.root / f"case-{index}" / "skills"
                self.skills.mkdir(parents=True)
                for path in paths:
                    self.skill(path)
                with self.assertRaises(ValueError):
                    validator.discover_skills(self.skills)

    def test_rejects_skill_beyond_one_group_level(self):
        self.skill("engineering/backend/wd-review")
        with self.assertRaises(ValueError):
            validator.discover_skills(self.skills)

    def test_rejects_a_skill_that_also_contains_another_entrypoint(self):
        self.skill("wd-review")
        self.skill("wd-review/wd-child")
        with self.assertRaises(ValueError):
            validator.discover_skills(self.skills)

    def test_allows_deep_resource_directories_inside_a_leaf_skill(self):
        directory = self.skill("engineering/wd-review")
        self.write(directory / "references" / "examples" / "nested" / "guide.md")
        self.write(directory / "README.md", "[Guide](references/examples/nested/guide.md)\n")

        self.assertEqual(validator.discover_skills(self.skills), [directory])
        self.assertEqual(validator.check_skill(directory), [])

    def test_requires_lowercase_namespaced_name_matching_the_leaf(self):
        self.assertEqual(validator.check_skill(self.skill("wd-valid")), [])
        for name in ("review", "WD-review", "wd-Review", "wd-"):
            with self.subTest(name=name):
                self.assertTrue(validator.check_skill(self.skill(name)))
        mismatched = self.skill("wd-folder", name="wd-different")
        self.assertTrue(validator.check_skill(mismatched))

    def test_requires_a_per_skill_readme(self):
        directory = self.skill("wd-review", readme=False)
        self.assertTrue(validator.check_skill(directory))
        self.write(directory / "README.md")
        self.assertEqual(validator.check_skill(directory), [])

    def test_ignores_links_written_as_markdown_code(self):
        directory = self.skill("wd-review")
        cases = {
            "inline": "`[example](missing.md)`\n",
            "two ticks": "``[example](missing.md) with a ` character``\n",
            "three ticks": "```[example](missing.md) with `` characters```\n",
            "backtick fence": "```markdown\n[example](missing.md)\n```\n",
            "tilde fence": "~~~markdown\n[example](missing.md)\n~~~\n",
            "long fence": "````markdown\n```\n[example](missing.md)\n```\n````\n",
            "indented": "    [example](missing.md)\n",
        }
        document = directory / "examples.md"
        for label, text in cases.items():
            with self.subTest(kind=label):
                self.write(document, text)
                self.assertEqual(validator.check_links(document, directory), [])

    def test_checks_real_links_after_code_and_with_code_formatted_labels(self):
        directory = self.skill("wd-review")
        document = self.write(
            directory / "examples.md",
            "```markdown\n[example](code-only.md)\n```\n\n"
            "`[inline example](also-code-only.md)` [Real](missing-real.md)\n\n"
            "[`code label`](missing-label.md)\n",
        )
        errors = validator.check_links(document, directory)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("missing-real.md" in error for error in errors))
        self.assertTrue(any("missing-label.md" in error for error in errors))
        self.assertFalse(any("code-only.md" in error for error in errors))

    def test_checks_reference_style_links(self):
        directory = self.skill("wd-review")
        self.write(directory / "guide.md")
        document = self.write(
            directory / "references.md",
            "[Existing][guide]\n\n[Missing][absent]\n\n"
            "[guide]: guide.md\n[absent]: missing-reference.md\n",
        )
        errors = validator.check_links(document, directory)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing-reference.md", errors[0])

    def test_checks_local_images(self):
        directory = self.skill("wd-review")
        self.write(directory / "assets" / "diagram.svg", "<svg/>\n")
        document = self.write(
            directory / "images.md",
            "![Existing](assets/diagram.svg)\n\n![Missing][diagram]\n\n"
            "[diagram]: assets/missing.svg\n",
        )
        errors = validator.check_links(document, directory)
        self.assertEqual(len(errors), 1)
        self.assertIn("assets/missing.svg", errors[0])

    def test_accepts_existing_encoded_local_targets_fragments_and_external_links(self):
        directory = self.skill("wd-review")
        self.write(directory / "guide notes.md")
        document = self.write(
            directory / "links.md",
            "[Local](guide%20notes.md#usage)\n[Section](#usage)\n"
            "[Remote](https://example.com/guide)\n[Email](mailto:review@example.com)\n",
        )
        self.assertEqual(validator.check_links(document, directory), [])

    def test_rejects_plain_and_encoded_traversal_to_an_existing_file(self):
        directory = self.skill("wd-review")
        self.write(self.skills / "outside.md")
        document = directory / "links.md"
        for target in ("../outside.md", "%2e%2e/outside.md"):
            with self.subTest(target=target):
                self.write(document, f"[Outside]({target})\n")
                errors = validator.check_links(document, directory)
                self.assertEqual(len(errors), 1)

    def test_rejects_symlink_escape_even_without_a_markdown_reference(self):
        directory = self.skill("wd-review")
        outside = self.write(self.root / "outside.md")
        link = directory / "escape.md"
        try:
            link.symlink_to(outside)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"Symlinks unavailable: {error}")

        self.assertTrue(validator.check_skill(directory))
        document = self.write(directory / "links.md", "[Outside](escape.md)\n")
        self.assertTrue(validator.check_links(document, directory))

    def test_full_validation_checks_skill_and_repository_document_links(self):
        directory = self.skill("engineering/wd-review")
        self.write(self.root / "README.md", "[Review](skills/engineering/wd-review/README.md)\n")
        self.write(self.root / "CONTRIBUTING.md")
        self.write(self.root / "tests" / "README.md")

        discovered, errors = validator.validate_package(self.root)
        self.assertEqual(discovered, [directory])
        self.assertEqual(errors, [])

        self.write(directory / "README.md", "[Missing](missing-skill-guide.md)\n")
        self.write(self.root / "README.md", "[Missing](missing-catalog-target.md)\n")
        discovered, errors = validator.validate_package(self.root)
        self.assertEqual(discovered, [directory])
        self.assertTrue(any("missing-skill-guide.md" in error for error in errors))
        self.assertTrue(any("missing-catalog-target.md" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
