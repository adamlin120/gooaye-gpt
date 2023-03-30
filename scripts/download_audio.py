import os
import re
import xml.etree.ElementTree as ET

import requests
from tqdm import tqdm


def main():
    # download directory
    download_dir = "audio"

    # URL of the RSS feed
    rss_url = (
        "https://feeds.soundon.fm/podcasts/954689a5-3096-43a4-a80b-7810b219cef3.xml"
    )

    # Download the RSS feed
    response = requests.get(rss_url)
    xml_data = response.content

    # Parse the XML data
    root = ET.fromstring(xml_data)

    mp3_urls = {}
    for item in tqdm(root.findall("./channel/item")):
        # Get episode number and MP3 URL
        title = item.find("title").text.strip()
        episode_number = title.split("|")[0].strip().replace("EP", "").zfill(3)
        # extract only the numeric part of the episode number using regex
        episode_number = int(re.findall(r"\d+", title)[0])
        mp3_url = item.find("enclosure").get("url")

        mp3_urls[episode_number] = mp3_url

    assert len(mp3_urls) == max(mp3_urls.keys()), "Missing episode numbers"

    num_already_downloaded = sum(
        os.path.exists(f"{download_dir}/{episode_number}.mp3")
        for episode_number in mp3_urls
    )

    pbar = tqdm(total=len(mp3_urls) - num_already_downloaded)
    while True:
        for episode_number, mp3_url in mp3_urls.items():
            mp3_path = f"{download_dir}/{episode_number}.mp3"

            # if mp3 file already exists, skip
            if os.path.exists(mp3_path):
                continue

            # Download MP3 data
            try:
                response = requests.get(mp3_url)
            # all requests.exceptions
            except requests.exceptions.RequestException as e:
                continue
            mp3_data = response.content

            # create directory if it doesn't exist
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            # save mp3 file
            with open(mp3_path, "wb") as f:
                f.write(mp3_data)

            pbar.update(1)

        # if all mp3 files exist, break
        if all(
            os.path.exists(f"{download_dir}/{episode_number}.mp3")
            for episode_number in mp3_urls
        ):
            break


if __name__ == "__main__":
    main()
