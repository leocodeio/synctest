"""
Audio Analysis Service
Handles beat detection and tempo estimation using librosa
"""

import librosa
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple


class AudioService:
    """Service for analyzing audio files and extracting beat information"""

    @staticmethod
    def extract_beat_timestamps(audio_path: str) -> Dict:
        """
        Extract beat timestamps and tempo from an audio file using librosa.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing:
                - tempo: Estimated BPM (beats per minute)
                - beat_times: List of beat timestamps in seconds
                - beat_frames: List of beat frame indices
                - sample_rate: Sample rate of the audio
                - duration: Total duration of audio in seconds
        """
        # Load audio file
        y, sr = librosa.load(audio_path)
        
        # Calculate duration
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Track beats and estimate tempo
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        
        # Convert beat frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # Calculate beat intervals (duration between beats)
        beat_intervals = []
        for i in range(len(beat_times) - 1):
            beat_intervals.append(beat_times[i + 1] - beat_times[i])
        
        return {
            'tempo': float(tempo),
            'beat_times': beat_times.tolist(),
            'beat_frames': beat_frames.tolist(),
            'beat_intervals': beat_intervals,
            'sample_rate': int(sr),
            'duration': float(duration),
            'num_beats': len(beat_times)
        }
    
    @staticmethod
    def save_beat_data(beat_data: Dict, output_path: str) -> None:
        """
        Save beat data to a JSON file.
        
        Args:
            beat_data: Dictionary containing beat information
            output_path: Path to save the JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(beat_data, f, indent=2)
    
    @staticmethod
    def load_beat_data(input_path: str) -> Dict:
        """
        Load beat data from a JSON file.
        
        Args:
            input_path: Path to the JSON file
            
        Returns:
            Dictionary containing beat information
        """
        with open(input_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def get_beat_intervals(beat_data: Dict) -> List[Tuple[float, float]]:
        """
        Get intervals between beats as (start_time, end_time) tuples.
        
        Args:
            beat_data: Dictionary containing beat information
            
        Returns:
            List of (start_time, end_time) tuples for each beat interval
        """
        beat_times = beat_data['beat_times']
        intervals = []
        
        for i in range(len(beat_times) - 1):
            intervals.append((beat_times[i], beat_times[i + 1]))
        
        return intervals
