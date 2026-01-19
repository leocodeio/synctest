# Video Processing

This file contains information related to intelligent video segmentation and processing for the beat‑synced video pipeline.

## Intelligent Video Segmentation

Instead of randomly selecting video segments, we use **content-aware analysis** to automatically find the best clips that match beat durations.

### Scene Detection
- Uses **PySceneDetect** to identify natural scene boundaries in raw videos.
- Detects cuts, transitions, and scene changes automatically.
- Methods:
  - `ContentDetector`: Analyzes frame differences to detect jump cuts
  - `AdaptiveDetector`: Uses rolling average for better fast-motion handling
  
### Motion Intensity Analysis
- Uses **OpenCV** to calculate motion intensity in video segments.
- Techniques:
  - **Optical Flow (Farneback)**: Computes motion vectors for every pixel
  - **Frame Differencing**: Detects changes between consecutive frames
- Scores segments based on action/movement level

### Quality Scoring System
For each detected scene, calculate a composite score based on:
1. **Motion Score**: Higher motion = more dynamic/engaging
2. **Duration Match**: How well the scene duration matches the beat interval
3. **Visual Quality**: Sharpness, contrast, brightness analysis

### Segment Selection Algorithm
```python
def select_best_segments(video_path, beat_durations):
    """
    Automatically select the best video segments matching beat durations.
    
    Args:
        video_path: Path to raw video file
        beat_durations: List of durations between beats [d1, d2, d3, ...]
    
    Returns:
        List of (start_time, end_time, score) tuples for best segments
    """
    # 1. Detect all scenes using PySceneDetect
    scenes = detect_scenes(video_path)
    
    # 2. Analyze motion intensity for each scene
    for scene in scenes:
        scene['motion_score'] = calculate_motion_intensity(video_path, scene)
    
    # 3. For each beat duration, find best matching scene
    selected_segments = []
    for duration in beat_durations:
        best_scene = find_best_match(scenes, duration)
        selected_segments.append(best_scene)
    
    return selected_segments
```

## Implementation Details

### Dependencies
```bash
pip install scenedetect[opencv] opencv-python moviepy numpy
```

### Scene Detection with PySceneDetect
```python
from scenedetect import detect, ContentDetector, AdaptiveDetector

def detect_scenes(video_path):
    """Detect scenes in video using content-aware detection."""
    scene_list = detect(video_path, ContentDetector())
    return scene_list
```

### Motion Intensity Calculation
```python
import cv2
import numpy as np

def calculate_motion_intensity(video_path, scene):
    """Calculate motion intensity using optical flow."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, scene['start_frame'])
    
    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    motion_scores = []
    
    while cap.get(cv2.CAP_PROP_POS_FRAMES) < scene['end_frame']:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Calculate magnitude of motion
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        motion_scores.append(np.mean(magnitude))
        
        prev_gray = gray
    
    cap.release()
    return np.mean(motion_scores)
```

### Segment Matching Algorithm
```python
def find_best_match(scenes, target_duration, tolerance=0.5):
    """
    Find the best scene matching the target duration.
    
    Args:
        scenes: List of detected scenes with motion scores
        target_duration: Desired duration in seconds
        tolerance: Acceptable duration variance (±seconds)
    
    Returns:
        Best matching scene with highest composite score
    """
    candidates = []
    
    for scene in scenes:
        duration = scene['end_time'] - scene['start_time']
        
        # Check if duration is within tolerance
        if abs(duration - target_duration) <= tolerance:
            # Calculate composite score
            duration_match = 1.0 - (abs(duration - target_duration) / tolerance)
            motion_score = scene['motion_score']
            
            composite_score = (0.6 * motion_score) + (0.4 * duration_match)
            
            candidates.append({
                'scene': scene,
                'score': composite_score
            })
    
    # Return scene with highest score
    if candidates:
        best = max(candidates, key=lambda x: x['score'])
        return best['scene']
    
    # Fallback: return closest duration match
    return min(scenes, key=lambda s: abs((s['end_time'] - s['start_time']) - target_duration))
```

## References
- [PySceneDetect Documentation](https://scenedetect.com/)
- [OpenCV Optical Flow Tutorial](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html)
- [MoviePy Documentation](https://moviepy.readthedocs.io/en/latest/)
- [FFmpeg Official Site](https://ffmpeg.org/)
