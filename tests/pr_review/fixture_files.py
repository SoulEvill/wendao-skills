"""File helpers for reproducible review fixtures."""

import hashlib
import json
from pathlib import Path


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def digest(path):
    """Hash one generated fixture file for reproducibility checks."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
