"""
Assembly Service
Handles video assembly and composition using MoviePy v2
"""

from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from typing import List, Dict
from pathlib import Path


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

        # Load videos once
        video_map = {p: VideoFileClip(p) for p in video_paths}
        clips = []

        try:
            # ----------------------------------
            # Build clips from selected segments
            # ----------------------------------
            for seg in selected_segments:
                target = seg.get("target_duration", 0)
                seg_clips = []

                for sc in seg.get("scenes", []):
                    vp = sc.get("video_path")
                    if vp not in video_map:
                        continue

                    src = video_map[vp]

                    start = max(0, sc["start_time"])
                    end = min(sc["end_time"], src.duration)

                    if end - start < 0.05:
                        continue

                    clip = src.subclipped(start, end)
                    seg_clips.append(clip)

                # Trim last clip if segment exceeds target duration
                total = sum(c.duration for c in seg_clips)
                if seg_clips and target > 0 and total > target:
                    excess = total - target
                    last = seg_clips[-1]
                    seg_clips[-1] = last.subclipped(
                        0, max(0.05, last.duration - excess)
                    )

                clips.extend(seg_clips)

            # ----------------------------------
            # 🔥 HARD FALLBACK (never crash)
            # ----------------------------------
            if not clips and video_map:
                print("⚠️ Assembly fallback: using first video")
                v = list(video_map.values())[0]
                clips.append(v.subclipped(0, min(2.0, v.duration)))

            if not clips:
                raise ValueError("No usable video clips found")

            # ----------------------------------
            # Concatenate video
            # ----------------------------------
            video = concatenate_videoclips(clips, method=method)

            # ----------------------------------
            # Attach audio safely
            # ----------------------------------
            audio = AudioFileClip(audio_path)
            duration = min(video.duration, audio.duration)

            video = video.subclipped(0, duration)
            audio = audio.subclipped(0, duration)

            final = video.with_audio(audio)

            # ----------------------------------
            # Write output
            # ----------------------------------
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)

            final.write_videofile(
                str(out),
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True
            )

            return str(out)

        finally:
            # Always release video resources
            for v in video_map.values():
                try:
                    v.close()
                except Exception:
                    pass