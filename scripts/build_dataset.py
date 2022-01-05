import json
import os
import argparse
from datetime import datetime
from typing import Tuple

from tqdm import tqdm

from scripts.image_scraping import scrape_and_download_thumbnails


TIME = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def build(size: Tuple[int, int], samples: int):
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", help="Final size (width, height) of the images", type=int, nargs=2, required=True)
    parser.add_argument("--samples", help="Number of samples per celebrity to download", type=int, default=50)

    args = parser.parse_args()

    build(args.size, args.samples)
