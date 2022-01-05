import json
import os
from datetime import datetime

from tqdm import tqdm

from scripts.image_scraping import scrape_and_download_thumbnails


TIME = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def build():
    root = f"data/images/{TIME}"
    os.mkdir(root)

    with open("data/celebrities_seasons.json") as fid:
        seasons = json.load(fid)

    for i, (season, celebs) in enumerate(seasons.items(), 1):
        print(f"{season} ({i}/{len(seasons.items())})")
        dst_dir = f"{root}/{season}"
        os.mkdir(dst_dir)
        for celeb in tqdm(celebs):
            scrape_and_download_thumbnails(celeb, dst_dir)


if __name__ == "__main__":
    build()
