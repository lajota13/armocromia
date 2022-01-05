import logging
import glob
import os
import argparse
from typing import List
from threading import Thread

from PIL import Image
import numpy as np
from mtcnn import MTCNN
from tqdm import tqdm


WORKERS_NUM = 8


def init_logger(path: str):
    logger = logging.getLogger(__name__)
    fh = logging.FileHandler(path)
    logger.addHandler(fh)
    return logger


class Cropper(Thread):
    def __init__(self, paths: List[str], dst_root: str, pbar: tqdm, logger: logging.Logger):
        self.paths = paths
        self.dst_root = dst_root
        self.detector = MTCNN()
        self.pbar = pbar
        self.logger = logger
        super().__init__()

    def run(self):
        for p in self.paths:
            self.preprocess(p)

    def preprocess(self, path: str):
        try:
            img = Image.open(path)
            faces = self.detector.detect_faces(np.array(img))
            if len(faces) == 1:
                x, y, w, h = faces[0]["box"]
                img_crop = img.crop((x, y, x + w, y + h))
                img.close()
                dst_path = "/".join([self.dst_root] + path.split("/")[-2:])
                img_crop.save(dst_path)
                img_crop.close()
            else:
                img.close()
            self.pbar.update(1)
        except:
            self.logger.exception(f"Could not preprocess {path}")
            self.pbar.update(1)


def split_paths(paths: List[str], n: int) -> List[List[str]]:
    dim = len(paths) // n
    chunks = []
    for i in range(n - 1):
        chunks.append(paths[i * dim: (i + 1) * dim])
    chunks.append(paths[(i + 1) * dim:])
    return chunks


def preprocess_season(season_dir: str, dst_root: str, logger):
    paths = glob.glob(season_dir + "/*.png")
    chunks = split_paths(paths, WORKERS_NUM)
    with tqdm(total=len(paths)) as pbar:
        croppers = [Cropper(c, dst_root, pbar, logger) for c in chunks]
        for c in croppers:
            c.start()
        for c in croppers:
            c.join()


def preprocess_dataset(src_root: str):
    dst_root = f"{src_root}_preprocessed"
    os.mkdir(dst_root)
    logger = init_logger(dst_root + "/exceptions.log")
    seasons_dirs = glob.glob(src_root + "/*/")
    for i, season_dir in enumerate(seasons_dirs, 1):
        os.mkdir(dst_root + "/" + season_dir.split("/")[-2])
        print(f"{season_dir.split('/')[-1]} ({i}/{len(seasons_dirs)})")
        preprocess_season(season_dir, dst_root, logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_dataset", help="Directory of the dataset", required=True)

    args = parser.parse_args()

    preprocess_dataset(args.src_dataset)
