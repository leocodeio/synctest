"""
Video Analysis Service
Handles scene detection and motion analysis using PySceneDetect and OpenCV
"""

import cv2
import numpy as np
from scenedetect import open_video, SceneManager, ContentDetector
from typing import List, Dict, Tuple
from pathlib import Path


class VideoService:
    """Service for analyzing video files and extracting scene information"""

    @staticmethod
    def detect_scenes(video_path: str, threshold: float = 27.0) -> List[Dict]:
        """
        Detect scenes in a video using PySceneDetect ContentDetector.
        
        Args:
            video_path: Path to the video file
            threshold: Sensitivity threshold for scene detection (lower = more sensitive)
            
        Returns:
            List of dictionaries containing scene information:
                - start_time: Start time in seconds
                - end_time: End time in seconds
                - start_frame: Start frame number
                - end_frame: End frame number
                - duration: Scene duration in seconds
        """
        # Open video and create scene manager
        video = open_video(video_path)
        scene_manager = SceneManager()
        
        # Add ContentDetector
        scene_manager.add_detector(ContentDetector(threshold=threshold))
        
        # Detect scenes
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()
        
        # Convert to dictionary format
        scenes = []
        for i, (start, end) in enumerate(scene_list):
            scenes.append({
                'scene_id': i,
                'start_time': start.get_seconds(),
                'end_time': end.get_seconds(),
                'start_frame': start.get_frames(),
                'end_frame': end.get_frames(),
                'duration': end.get_seconds() - start.get_seconds()
            })
        
        return scenes
    
    @staticmethod
    def calculate_motion_intensity(video_path: str, start_frame: int, end_frame: int) -> float:
        """
        Calculate motion intensity for a video segment using optical flow.
        
        Args:
            video_path: Path to the video file
            start_frame: Starting frame number
            end_frame: Ending frame number
            
        Returns:
            Average motion intensity (magnitude) for the segment
        """
        cap = cv2.VideoCapture(video_path)
        
        # Set starting frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Read first frame
        ret, frame1 = cap.read()
        if not ret:
            return 0.0
        
        prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        
        motion_magnitudes = []
        frame_count = 0
        
        # Process frames in the segment
        for frame_num in range(start_frame + 1, min(end_frame, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
            ret, frame2 = cap.read()
            if not ret:
                break
            
            next_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate dense optical flow using Farneback method
            flow = cv2.calcOpticalFlowFarneback(
                prvs, next_frame, None, 
                pyr_scale=0.5, 
                levels=3, 
                winsize=15, 
                iterations=3, 
                poly_n=5, 
                poly_sigma=1.2, 
                flags=0
            )
            
            # Calculate magnitude
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            motion_magnitudes.append(np.mean(mag))
            
            prvs = next_frame
            frame_count += 1
        
        cap.release()
        
        # Return average motion intensity
        return float(np.mean(motion_magnitudes)) if motion_magnitudes else 0.0
    
    @staticmethod
    def score_scene(motion_intensity: float, duration: float, target_duration: float) -> float:
        """
        Score a scene based on motion intensity and duration match.
        
        Args:
            motion_intensity: Motion intensity value from calculate_motion_intensity
            duration: Actual duration of the scene
            target_duration: Target duration to match (from beat interval)
            
        Returns:
            Score value (higher is better)
        """
        # Motion score (normalized, weighted 60%)
        motion_score = min(motion_intensity / 10.0, 1.0) * 0.6
        
        # Duration match score (weighted 40%)
        duration_diff = abs(duration - target_duration)
        duration_score = max(0, 1.0 - (duration_diff / target_duration)) * 0.4
        
        return motion_score + duration_score
    
    @staticmethod
    def analyze_scenes_with_motion(video_path: str, scenes: List[Dict]) -> List[Dict]:
        """
        Analyze scenes and add motion intensity scores.
        
        Args:
            video_path: Path to the video file
            scenes: List of scene dictionaries from detect_scenes
            
        Returns:
            List of scenes with added 'motion_intensity' field
        """
        analyzed_scenes = []
        
        for scene in scenes:
            motion = VideoService.calculate_motion_intensity(
                video_path,
                scene['start_frame'],
                scene['end_frame']
            )
            
            scene_copy = scene.copy()
            scene_copy['motion_intensity'] = motion
            analyzed_scenes.append(scene_copy)
        
        return analyzed_scenes
    
    @staticmethod
    def select_best_segments(scenes: List[Dict], beat_intervals: List[Tuple[float, float]]) -> List[Dict]:
        """
        Select best video segments to match beat intervals.
        
        Args:
            scenes: List of analyzed scenes with motion intensity
            beat_intervals: List of (start_time, end_time) tuples from audio analysis
            
        Returns:
            List of selected segments with their scores
        """
        selected_segments = []
        
        for beat_start, beat_end in beat_intervals:
            target_duration = beat_end - beat_start
            best_scene = None
            best_score = -1
            
            # Find best matching scene
            for scene in scenes:
                score = VideoService.score_scene(
                    scene.get('motion_intensity', 0),
                    scene['duration'],
                    target_duration
                )
                
                if score > best_score:
                    best_score = score
                    best_scene = scene
            
            if best_scene:
                selected_segments.append({
                    'scene': best_scene,
                    'target_duration': target_duration,
                    'score': best_score,
                    'beat_start': beat_start,
                    'beat_end': beat_end
                })
        
        return selected_segments
