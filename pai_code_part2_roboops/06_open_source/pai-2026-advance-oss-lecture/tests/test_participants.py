from pathlib import Path

import pytest

from pai_oss_lecture.participants import (
    PARTICIPANTS_DIR,
    load_participants,
    validate_participant,
)

PARTICIPANT_FILES = sorted(p for p in PARTICIPANTS_DIR.iterdir() if p.name != "README.md")


@pytest.mark.parametrize("path", PARTICIPANT_FILES, ids=lambda p: p.name)
def test_participant_file_is_valid(path: Path) -> None:
    errors = validate_participant(path)
    assert not errors, "\n".join(errors)


def test_github_usernames_are_unique_case_insensitive() -> None:
    names = [p.stem.lower() for p in PARTICIPANT_FILES]
    duplicates = {n for n in names if names.count(n) > 1}
    assert not duplicates, f"duplicate participants: {sorted(duplicates)}"


def test_load_participants() -> None:
    participants = load_participants()
    assert participants
    assert all(p.github for p in participants)


def _write(tmp_path: Path, filename: str, content: str) -> Path:
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    return path


def test_validate_accepts_valid_file(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "octocat.toml",
        'name = "Octo Cat"\ngithub = "octocat"\nmessage = "Hello!"\nfavorite_oss = "git"\n',
    )
    assert validate_participant(path) == []


@pytest.mark.parametrize(
    ("filename", "content", "expected"),
    [
        ("octocat.toml", 'name = "a"\ngithub = "octocat"\n', "missing keys"),
        ("octocat.toml", 'name = "a"\ngithub = "someone"\nmessage = "hi"\n', "must match"),
        ("octocat.toml", 'name = "a"\ngithub = "octocat"\nmessage = "hi"\nage = 20\n', "unknown"),
        ("octocat.toml", 'name = ""\ngithub = "octocat"\nmessage = "hi"\n', "non-empty"),
        ("octocat.toml", f'name = "a"\ngithub = "octocat"\nmessage = "{"a" * 141}"\n', "at most"),
        ("octocat.toml", 'name = "a"\ngithub = "octocat"\nmessage = "hi\n', "invalid TOML"),
        ("-octocat.toml", 'name = "a"\ngithub = "-octocat"\nmessage = "hi"\n', "file name"),
        ("octocat.txt", "", "extension"),
    ],
)
def test_validate_rejects_invalid_file(
    tmp_path: Path, filename: str, content: str, expected: str
) -> None:
    errors = validate_participant(_write(tmp_path, filename, content))
    assert any(expected in e for e in errors), errors
