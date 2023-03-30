import os
from pathlib import Path

import pandas as pd
import whisper
from pydub import AudioSegment
from tqdm import tqdm


def main():
    model = whisper.load_model("large-v2")

    audio_dir = "audio"

    # index: episode, start other columns: transcript
    if os.path.exists("transcript.csv"):
        df = pd.read_csv("transcript.csv")
    else:
        df = pd.DataFrame(columns=["episode", "start", "transcript"])

    for mp3_path in tqdm(list(Path(audio_dir).glob("*.mp3"))):
        # load mp3 in audio waveform in numpy.ndarray
        mp3_segment = AudioSegment.from_mp3(mp3_path)
        episode_number = mp3_path.stem

        # Split AudioSegment into 1-minute segments
        segment_duration = 1000 * 60

        for i, segment in tqdm(
            enumerate(mp3_segment[::segment_duration]),
            total=len(mp3_segment) // segment_duration,
        ):
            start_in_sec = i * segment_duration // 1000

            if (
                df.query(
                    f"episode == '{episode_number}' and start == {start_in_sec}"
                ).shape[0]
                > 0
            ):
                continue

            # save to tmp.mp3
            segment.export("tmp.mp3", format="mp3")

            # transcribe audio segment using model.transcribe(audio_waveform_in_numpy)
            transcript = model.transcribe("tmp.mp3")["text"]

            # append to dataframe
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "episode": [episode_number],
                            "start": [start_in_sec],
                            "transcript": [transcript],
                        }
                    ),
                ],
                ignore_index=True,
            )

            df.to_csv("transcript.csv", index=False)

    os.remove("tmp.mp3")


if __name__ == "__main__":
    main()
