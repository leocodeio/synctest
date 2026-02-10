"""
Audio Analysis Service
Handles beat detection and musically meaningful beat grouping using librosa
"""

import librosa
from typing import Dict, List, Tuple


class AudioService:
    """Service for analyzing audio files and extracting beat information"""

    @staticmethod
    def extract_beat_timestamps(audio_path: str) -> Dict:
        y, sr = librosa.load(audio_path)

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        duration = float(librosa.get_duration(y=y, sr=sr))

        return {
            "tempo": float(tempo),
            "beat_times": beat_times.tolist(),
            "duration": duration,
            "num_beats": len(beat_times)
        }

    @staticmethod
    def get_beat_intervals(
        beat_data: Dict,
        min_segment_duration: float = 2.0
    ) -> List[Tuple[float, float]]:
        """
        Always generate intervals covering the FULL audio duration.
        Falls back to uniform slicing if beats are weak or missing.
        """

        duration = beat_data["duration"]
        beat_times = beat_data.get("beat_times", [])

        intervals: List[Tuple[float, float]] = []

        # 🔥 CASE 1: Weak / no beats → uniform slicing
        if len(beat_times) < 4:
            t = 0.0
            while t < duration:
                intervals.append((t, min(t + min_segment_duration, duration)))
                t += min_segment_duration
            return intervals

        # 🔥 CASE 2: Normal beats → grouped beats
        start = beat_times[0]
        for t in beat_times[1:]:
            if t - start >= min_segment_duration:
                intervals.append((start, t))
                start = t

        # 🔥 FORCE last segment to reach audio end
        if start < duration:
            intervals.append((start, duration))

        return intervals