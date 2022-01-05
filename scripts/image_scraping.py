from typing import List
from io import BytesIO
import re
import json

from PIL import Image
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}
SIZE = (224, 224)


def scrape_thumbnails(query: str) -> List[str]:
    params = {
        "q": query,
        "tbm": "isch",
        "ijn": "0",
    }
    html = requests.get("https://www.google.com/search", params=params, headers=HEADERS)
    soup = BeautifulSoup(html.text, 'lxml')

    # this steps could be refactored to a more compact
    all_script_tags = soup.select('script')

    # # https://regex101.com/r/48UZhY/4
    matched_images_data = ''.join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))

    # https://kodlogs.com/34776/json-decoder-jsondecodeerror-expecting-property-name-enclosed-in-double-quotes
    # if you try to json.loads() without json.dumps it will throw an error:
    # "Expecting property name enclosed in double quotes"
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    # https://regex101.com/r/pdZOnW/3
    matched_google_image_data = re.findall(r'\[\"GRID_STATE0\",null,\[\[1,\[0,\".*?\",(.*),\"All\",',
                                           matched_images_data_json)

    # https://regex101.com/r/NnRg27/1
    matched_google_images_thumbnails = ', '.join(
        re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                   str(matched_google_image_data))).split(', ')

    thumbnails = []
    for fixed_google_image_thumbnail in matched_google_images_thumbnails:
        # https://stackoverflow.com/a/4004439/15164646 comment by Frédéric Hamidi
        google_image_thumbnail_not_fixed = bytes(fixed_google_image_thumbnail, 'ascii').decode('unicode-escape')

        # after first decoding, Unicode characters are still present. After the second iteration, they were decoded.
        google_image_thumbnail = bytes(google_image_thumbnail_not_fixed, 'ascii').decode('unicode-escape')
        thumbnails.append(google_image_thumbnail)

    # # removing previously matched thumbnails for easier full resolution image matches.
    # removed_matched_google_images_thumbnails = re.sub(
    #     r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', '', str(matched_google_image_data))
    #
    # # https://regex101.com/r/fXjfb1/4
    # # https://stackoverflow.com/a/19821774/15164646
    # matched_google_full_resolution_images = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
    #                                                    removed_matched_google_images_thumbnails)
    #
    # print('\nFull Resolution Images:')  # in order
    # images = []
    # for index, fixed_full_res_image in enumerate(matched_google_full_resolution_images):
    #     # https://stackoverflow.com/a/4004439/15164646 comment by Frédéric Hamidi
    #     original_size_img_not_fixed = bytes(fixed_full_res_image, 'ascii').decode('unicode-escape')
    #     original_size_img = bytes(original_size_img_not_fixed, 'ascii').decode('unicode-escape')
    #     images.append(original_size_img)
    #     print(original_size_img)
    return thumbnails


def download_thumbnail(url: str, img_name: str):
    r = requests.get(url, headers=HEADERS)
    with Image.open(BytesIO(r.content)) as img:
        img.resize(SIZE).save(img_name, "PNG")


def download_thumbnails(urls: List[str], query: str):
    for i, url in enumerate(urls):
        q = query.replace(" ", "_")
        download_thumbnail(url, f"{q}_{i}.png")
