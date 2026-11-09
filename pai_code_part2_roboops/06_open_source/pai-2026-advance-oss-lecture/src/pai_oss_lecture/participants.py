"""Load and validate participant profiles under ``participants/``."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

PARTICIPANTS_DIR = Path(__file__).resolve().parents[2] / "participants"

REQUIRED_KEYS = {"name", "github", "message"}
OPTIONAL_KEYS = {"favorite_oss"}
MAX_MESSAGE_LENGTH = 140

# GitHub username: alphanumeric or single hyphens, cannot start/end with a hyphen, max 39 chars.
GITHUB_USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")


@dataclass(frozen=True)
class Participant:
    name: str
    github: str
    message: str
    favorite_oss: str | None = None


def validate_participant(path: Path) -> list[str]:
    """Return a list of problems found in ``path``. An empty list means the file is valid."""
    errors: list[str] = []

    if path.suffix != ".toml":
        return [f"{path.name}: extension must be .toml"]

    if not GITHUB_USERNAME_RE.match(path.stem):
        errors.append(f"{path.name}: file name must be your GitHub username (e.g. octocat.toml)")

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        return [*errors, f"{path.name}: invalid TOML ({e})"]

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        errors.append(f"{path.name}: missing keys {sorted(missing)}")

    unknown = data.keys() - REQUIRED_KEYS - OPTIONAL_KEYS
    if unknown:
        errors.append(f"{path.name}: unknown keys {sorted(unknown)}")

    for key in (REQUIRED_KEYS | OPTIONAL_KEYS) & data.keys():
        value = data[key]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{path.name}: '{key}' must be a non-empty string")

    github = data.get("github")
    if isinstance(github, str) and github != path.stem:
        errors.append(
            f"{path.name}: 'github' ({github!r}) must match the file name ({path.stem!r})"
        )

    message = data.get("message")
    if isinstance(message, str) and len(message) > MAX_MESSAGE_LENGTH:
        errors.append(
            f"{path.name}: 'message' must be at most {MAX_MESSAGE_LENGTH} characters "
            f"(got {len(message)})"
        )

    return errors


def load_participants(directory: Path = PARTICIPANTS_DIR) -> list[Participant]:
    """Load all participant profiles, sorted by GitHub username (case-insensitive)."""
    participants = []
    for path in sorted(directory.glob("*.toml"), key=lambda p: p.stem.lower()):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        participants.append(Participant(**data))
    return participants
