"""
Download all youtube video link from https://www.youtube.com/c/Gooaye
"""

import json
import re


def main():
    with open("video_link.txt") as f:
        lines = f.readlines()
    # lines example:
    # VM1005:1 	EP1 | 武漢肺炎 國外反亞情緒 股市崩盤	https://www.youtube.com/watch?v=xLS-2whm8Aw&t=111s
    # VM1005:1 	EP220 | 💃	https://www.youtube.com/watch?v=Z9nUjBAy2OI&t=111s
    # extract EP number (1, 220) and xLS-2whm8Aw, Z9nUjBAy2OI
    episode_to_youtube_id = {}
    for line in lines:
        line = line.strip("VM1005:1").strip()
        episode_number = int(re.findall(r"\d+", line)[0])
        youtube_id = line.split("https://www.youtube.com/watch?v=")[-1].strip()
        youtube_id = youtube_id.split("&")[0]
        print(f"EP{episode_number} \thttps://www.youtube.com/watch?v={youtube_id}")
        episode_to_youtube_id[episode_number] = youtube_id

    with open("episode_to_youtube_id.json", "w") as f:
        json.dump(episode_to_youtube_id, f, indent=4)


if __name__ == "__main__":
    main()
