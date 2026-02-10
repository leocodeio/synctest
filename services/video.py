"""
Video Analysis Service
Handles scene detection, motion analysis, and intelligent segment selection
"""

import cv2
import numpy as np
from scenedetect import open_video, SceneManager, ContentDetector
from typing import List, Dict, Tuple


class VideoService:

    @staticmethod
    def detect_scenes(video_path: str, threshold: float = 27.0) -> List[Dict]:
        video = open_video(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold))
        scene_manager.detect_scenes(video)

        scenes = []
        for i, (start, end) in enumerate(scene_manager.get_scene_list()):
            scenes.append({
                "scene_id": i,
                "start_time": start.get_seconds(),
                "end_time": end.get_seconds(),
                "start_frame": start.get_frames(),
                "end_frame": end.get_frames(),
                "duration": end.get_seconds() - start.get_seconds()
            })

        return scenes

    @staticmethod
    def calculate_motion_intensity(
        video_path: str,
        start_frame: int,
        end_frame: int
    ) -> float:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        ret, prev = cap.read()
        if not ret:
            cap.release()
            return 0.0

        prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
        mags = []

        for _ in range(start_frame + 1, end_frame):
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(
                prev, gray, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            mags.append(np.mean(mag))
            prev = gray

        cap.release()
        return float(np.mean(mags)) if mags else 0.0

    @staticmethod
    def analyze_scenes_with_motion(
        video_path: str,
        scenes: List[Dict]
    ) -> List[Dict]:
        out = []
        for s in scenes:
            m = VideoService.calculate_motion_intensity(
                video_path,
                s["start_frame"],
                s["end_frame"]
            )
            x = s.copy()
            x["motion_intensity"] = m
            x["video_path"] = video_path
            out.append(x)
        return out

    @staticmethod
    def select_best_segments(
        all_scenes: List[Dict],
        beat_intervals: List[Tuple[float, float]]
    ) -> List[Dict]:

        if not all_scenes or not beat_intervals:
            return []

        # Keep very short scenes (SceneDetect often produces small cuts)
        scenes = [s for s in all_scenes if s["duration"] >= 0.05]

        # 🔥 HARD fallback: never allow empty scenes
        if not scenes:
            scenes = all_scenes.copy()

        # Prefer high-motion scenes
        scenes.sort(
            key=lambda s: s.get("motion_intensity", 0),
            reverse=True
        )

        selected = []
        idx = 0

        for beat_start, beat_end in beat_intervals:
            target = beat_end - beat_start
            collected = []
            total = 0.0

            while total < target and scenes:
                scene = scenes[idx % len(scenes)]
                collected.append(scene)
                total += scene["duration"]
                idx += 1

            selected.append({
                "scenes": collected,
                "target_duration": target,
                "beat_start": beat_start,
                "beat_end": beat_end
            })

        return selected