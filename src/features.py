"""
features.py

This module handles feature extraction for audio segments.
It includes:
- MFCC, chroma, contrast, delta features (via librosa)
- Voice stress features: F0 mean, jitter, shimmer, HNR (via Parselmouth)
- Optional augmentation: time-stretch, pitch shift, Gaussian noise
"""

import numpy as np
import librosa
import parselmouth
import pandas as pd


def extract_features(filepath, n_mfcc=13, augment=False):
    """
    Extract audio features from a single file, with optional augmentation.

    Parameters:
        filepath (str): Path to the audio file
        n_mfcc (int): Number of MFCC coefficients to extract
        augment (bool): Whether to apply 3x augmentation

    Returns:
        List[np.ndarray]: List of feature vectors (original + augmented if enabled)
    """
    y, sr = librosa.load(filepath, sr=None)
    features = []

    def compute_feats(signal):
        # Handle very short audio
        if len(signal) < sr:  # less than 1 second
            return np.zeros(n_mfcc * 2 + 13 + 7 + 4)  # match expected dim

        # Librosa features
        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=n_mfcc)
        chroma = librosa.feature.chroma_stft(y=signal, sr=sr)
        contrast = librosa.feature.spectral_contrast(y=signal, sr=sr)
        delta = librosa.feature.delta(mfcc)

        # Parselmouth features
        try:
            snd = parselmouth.Sound(signal, sampling_frequency=sr)
            pitch = snd.to_pitch()
            point_process = parselmouth.praat.call(snd, "To PointProcess (periodic, cc)", 75, 500)

            f0_mean = pitch.get_mean()
            jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            shimmer = parselmouth.praat.call([snd, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            hnr = parselmouth.praat.call(snd, "Get harmonics-to-noise ratio", 0.0, 0.0)
        except Exception:
            f0_mean, jitter, shimmer, hnr = 0, 0, 0, 0

        return np.concatenate([
            np.mean(mfcc, axis=1),
            np.std(mfcc, axis=1),
            np.mean(delta, axis=1),
            np.mean(chroma, axis=1),
            np.mean(contrast, axis=1),
            np.array([f0_mean, jitter, shimmer, hnr])
        ])

    # Original audio
    features.append(compute_feats(y))

    if augment:
        # 1. Time-stretch
        try:
            y_stretch = librosa.effects.time_stretch(y, rate=1.1)
            features.append(compute_feats(y_stretch))
        except Exception:
            pass

        # 2. Pitch shift
        try:
            y_pitch = librosa.effects.pitch_shift(y, sr=sr, n_steps=-2)
            features.append(compute_feats(y_pitch))
        except Exception:
            pass

        # 3. Add noise
        y_noise = y + 0.005 * np.random.normal(0, 1, len(y))
        features.append(compute_feats(y_noise))

    return features


def extract_features_batch(df, path_column="segment_path", n_mfcc=13, augment=False):
    """
    Batch feature extraction for a DataFrame of file paths.

    Parameters:
        df (pd.DataFrame): DataFrame with audio file paths (and optionally labels)
        path_column (str): Column name for file paths
        n_mfcc (int): Number of MFCCs
        augment (bool): Whether to augment (creates 4 rows per file)

    Returns:
        pd.DataFrame: Feature vectors with label and filepath
    """
    all_features = []
    all_labels = []
    all_files = []

    for _, row in df.iterrows():
        filepath = row[path_column]
        label = row.get("label", None)

        try:
            feats_list = extract_features(filepath, n_mfcc=n_mfcc, augment=augment)

            for feats in feats_list:
                all_features.append(feats)
                all_labels.append(label)
                all_files.append(filepath)
        except Exception as e:
            print(f"[Warning] Skipping {filepath} — {e}")
            continue

    if not all_features:
        raise ValueError("No features extracted — check your input paths or files.")

    feature_names = [f"f{i+1}" for i in range(len(all_features[0]))]
    result_df = pd.DataFrame(all_features, columns=feature_names)
    result_df["label"] = all_labels
    result_df["filepath"] = all_files

    return result_df
