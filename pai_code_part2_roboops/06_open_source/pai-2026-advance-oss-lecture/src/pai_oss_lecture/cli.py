"""Print the list of participants who have contributed to this repository."""

from pai_oss_lecture.participants import load_participants


def main() -> None:
    participants = load_participants()
    print(f"🎉 {len(participants)} contributors\n")
    for p in participants:
        line = f"- {p.name} (@{p.github}): {p.message}"
        if p.favorite_oss:
            line += f"  [favorite OSS: {p.favorite_oss}]"
        print(line)


if __name__ == "__main__":
    main()
