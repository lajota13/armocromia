import json
import re


def clean_line(line: str) -> str:
    m = re.match(r"[a-zÀ-ÿ]+\b", line, re.IGNORECASE)
    assert m is not None, f"No match found for {line}"
    return m.group()


def convert():
    with open("data/celebrities_seasons.txt", "r") as fid:
        lines = fid.read().split("\n")
    lines = [l for l in lines if l != ""]
    seasons = {}
    for line in lines:
        if line.startswith("-"):
            season = re.search(r"[A-Z ]+\b", line).group()
            season = season.strip().replace(" ", "_")
            seasons[season] = []
        else:
            seasons[season].append(clean_line(line))
    with open("data/celebrities_seasons.json", "w") as fid:
        json.dump(seasons, fid)


if __name__ == "__main__":
    convert()
