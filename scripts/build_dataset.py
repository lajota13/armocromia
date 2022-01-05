import json
import os
from datetime import datetime

from tqdm import tqdm

from scripts.image_scraping import scrape_and_download_thumbnails


N = 100
TIME = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def build():
    root = f"data/images/{TIME}"
    os.mkdir(root)

    with open("data/celebrities_seasons.json") as fid:
        seasons = json.load(fid)

    freq = {k: len(v) for k, v in seasons.items()}
    min_freq = min(freq.values())

    for i, (season, celebs) in enumerate(seasons.items(), 1):
        print(f"{season} ({i}/{len(seasons.items())})")
        dst_dir = f"{root}/{season}"
        os.mkdir(dst_dir)
        n = min_freq * N // len(celebs)
        for celeb in tqdm(celebs):
            scrape_and_download_thumbnails(celeb, dst_dir, n)


if __name__ == "__main__":
    build()
