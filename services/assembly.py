"""
Assembly Service
Handles video assembly and composition using MoviePy
"""

from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from typing import List, Dict
from pathlib import Path
import os


class AssemblyService:
    """Service for assembling video clips with synchronized audio"""

    @staticmethod
    def assemble_video(
        selected_segments: List[Dict],
        video_paths: List[str],
        audio_path: str,
        output_path: str,
        method: str = "compose"
    ) -> str:
        """
        Assemble final video from selected segments with synchronized audio.
        
        Args:
            selected_segments: List of segment dictionaries from VideoService.select_best_segments
            video_paths: List of paths to raw video files
            audio_path: Path to the music track
            output_path: Path for the output video file
            method: Concatenation method ('chain' or 'compose')
            
        Returns:
            Path to the generated video file
        """
        clips = []
        
        # Build a map of video paths for quick lookup
        video_map = {}
        for video_path in video_paths:
            video_map[video_path] = VideoFileClip(video_path)
        
        try:
            # Create clips from selected segments
            for segment in selected_segments:
                scene = segment['scene']
                target_duration = segment['target_duration']
                
                # Find which source video this scene came from
                # Note: In practice, you'd need to track which video each scene came from
                # For now, we'll use the first video path as default
                source_video = video_map[video_paths[0]]
                
                # Extract the clip
                start_time = scene['start_time']
                end_time = scene['end_time']
                
                # Adjust duration to match beat interval
                clip = source_video.subclip(start_time, end_time)
                
                # Resize or adjust duration if needed
                if abs(clip.duration - target_duration) > 0.1:
                    # Speed up or slow down to match target duration
                    speed_factor = clip.duration / target_duration
                    clip = clip.speedx(factor=speed_factor)
                
                clips.append(clip)
            
            # Concatenate all clips
            if clips:
                final_video = concatenate_videoclips(clips, method=method)
                
                # Overlay audio track
                audio = AudioFileClip(audio_path)
                
                # Trim audio to match video duration or loop if needed
                if audio.duration < final_video.duration:
                    # Loop audio if it's shorter
                    num_loops = int(final_video.duration / audio.duration) + 1
                    audio = concatenate_videoclips([audio] * num_loops).subclip(0, final_video.duration)
                else:
                    # Trim audio if it's longer
                    audio = audio.subclip(0, final_video.duration)
                
                final_video = final_video.set_audio(audio)
                
                # Write output file
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                final_video.write_videofile(
                    str(output_path),
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                return str(output_path)
            else:
                raise ValueError("No clips to assemble")
        
        finally:
            # Clean up loaded videos
            for video_clip in video_map.values():
                video_clip.close()
    
    @staticmethod
    def cut_clip(video_path: str, start_time: float, end_time: float, output_path: str) -> str:
        """
        Cut a specific segment from a video.
        
        Args:
            video_path: Path to the source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Path for the output clip
            
        Returns:
            Path to the cut clip
        """
        clip = VideoFileClip(video_path)
        
        try:
            cut = clip.subclip(start_time, end_time)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            cut.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac'
            )
            
            return str(output_path)
        
        finally:
            clip.close()
    
    @staticmethod
    def preview_segment(
        video_path: str,
        scene: Dict,
        beat_start: float,
        beat_end: float,
        output_path: str
    ) -> str:
        """
        Create a preview of a single segment with beat markers.
        
        Args:
            video_path: Path to the source video
            scene: Scene dictionary
            beat_start: Beat start time
            beat_end: Beat end time
            output_path: Path for the preview video
            
        Returns:
            Path to the preview video
        """
        return AssemblyService.cut_clip(
            video_path,
            scene['start_time'],
            scene['end_time'],
            output_path
        )
