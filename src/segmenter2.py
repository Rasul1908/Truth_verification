import os
import librosa
import soundfile as sf
import pandas as pd
from tqdm import tqdm

def segment_audio_files(csv_path, input_audio_dir, output_segment_dir, segment_duration=30):
    """
    Segments all audio files listed in the CSV into fixed-length chunks.
    
    Parameters:
        csv_path (str): Path to metadata CSV (must include 'filename', 'Language', 'Story_type')
        input_audio_dir (str): Folder containing .wav files
        output_segment_dir (str): Folder where segments will be saved
        segment_duration (int): Duration of each segment in seconds (default = 30)
        
    Returns:
        pd.DataFrame: Metadata of all segments including labels and original story metadata
    """
    
    os.makedirs(output_segment_dir, exist_ok=True)

    # Load and prepare metadata
    df = pd.read_csv(csv_path)
    df["Story_type"] = df["Story_type"].str.strip().str.lower()
    df["label"] = df["Story_type"].apply(lambda x: 1 if "true" in x else 0)

    segment_rows = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Segmenting audio"):
        filename = row["filename"]
        label = row["label"]
        language = row["Language"]
        story_type = row["Story_type"]

        filepath = os.path.join(input_audio_dir, filename)
        if not os.path.exists(filepath):
            print(f"Skipping missing file: {filename}")
            continue

        try:
            y, sr = librosa.load(filepath, sr=None)
            samples_per_segment = segment_duration * sr
            num_segments = int(len(y) / samples_per_segment)

            for i in range(num_segments):
                start_sample = int(i * samples_per_segment)
                end_sample = int((i + 1) * samples_per_segment)
                segment_audio = y[start_sample:end_sample]

                segment_filename = f"{os.path.splitext(filename)[0]}_seg{i+1}.wav"
                segment_path = os.path.join(output_segment_dir, segment_filename)
                sf.write(segment_path, segment_audio, sr)

                segment_rows.append({
                    "original_file": filename,
                    "segment_id": i + 1,
                    "segment_path": segment_path.replace("\\", "/"),
                    "duration": segment_duration,
                    "label": label,
                    "Language": language,
                    "Story_type": story_type,
                })

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    return pd.DataFrame(segment_rows)










