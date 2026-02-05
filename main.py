from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List, Dict
import uuid
import json
import shutil

from services.audio import AudioService
from services.video import VideoService
from services.assembly import AssemblyService


app = FastAPI(
    title="Beat-Synced Video Generator",
    description="Intelligent video segmentation and assembly synchronized to music beats",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="public"), name="static")

# Job storage (in-memory for now, use database in production)
jobs: Dict[str, Dict] = {}

# Ensure temp directories exist
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
(TEMP_DIR / "uploads").mkdir(exist_ok=True)
(TEMP_DIR / "outputs").mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main application HTML"""
    html_path = Path("public") / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload an audio file for processing"""
    if not file.filename.endswith(('.mp3', '.wav', '.m4a', '.flac')):
        raise HTTPException(status_code=400, detail="Invalid audio file format")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    audio_path = TEMP_DIR / "uploads" / f"{job_id}_audio_{file.filename}"
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Initialize job
    jobs[job_id] = {
        "id": job_id,
        "status": "audio_uploaded",
        "audio_path": str(audio_path),
        "video_paths": [],
        "progress": 10
    }
    
    return {"job_id": job_id, "status": "audio_uploaded"}


@app.post("/api/upload/video/{job_id}")
async def upload_video(job_id: str, file: UploadFile = File(...)):
    """Upload a video file for processing"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not file.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video file format")
    
    # Save uploaded file
    video_path = TEMP_DIR / "uploads" / f"{job_id}_video_{len(jobs[job_id]['video_paths'])}_{file.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Add to job
    jobs[job_id]["video_paths"].append(str(video_path))
    jobs[job_id]["progress"] = 20
    
    return {
        "job_id": job_id,
        "videos_uploaded": len(jobs[job_id]["video_paths"]),
        "status": "video_uploaded"
    }


def process_video_generation(job_id: str):
    """Background task to process video generation"""
    try:
        job = jobs[job_id]
        job["status"] = "processing"
        job["progress"] = 30
        
        # Step 1: Extract beat timestamps
        job["status"] = "analyzing_audio"
        audio_service = AudioService()
        beat_data = audio_service.extract_beat_timestamps(job["audio_path"])
        job["beat_data"] = beat_data
        job["progress"] = 40
        
        # Step 2: Detect scenes in videos
        job["status"] = "detecting_scenes"
        video_service = VideoService()
        all_scenes = []
        
        for video_path in job["video_paths"]:
            scenes = video_service.detect_scenes(video_path)
            # Analyze motion for each scene
            analyzed_scenes = video_service.analyze_scenes_with_motion(video_path, scenes)
            # Add video path to each scene
            for scene in analyzed_scenes:
                scene['video_path'] = video_path
            all_scenes.extend(analyzed_scenes)
        
        job["scenes"] = all_scenes
        job["progress"] = 60
        
        # Step 3: Select best segments
        job["status"] = "selecting_segments"
        beat_intervals = audio_service.get_beat_intervals(beat_data)
        selected_segments = video_service.select_best_segments(all_scenes, beat_intervals)
        job["selected_segments"] = selected_segments
        job["progress"] = 70
        
        # Step 4: Assemble video
        job["status"] = "assembling_video"
        output_path = TEMP_DIR / "outputs" / f"{job_id}_final.mp4"
        assembly_service = AssemblyService()
        
        final_video = assembly_service.assemble_video(
            selected_segments,
            job["video_paths"],
            job["audio_path"],
            str(output_path)
        )
        
        job["output_path"] = final_video
        job["status"] = "completed"
        job["progress"] = 100
        
    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        job["progress"] = 0


@app.post("/api/generate/{job_id}")
async def generate_video(job_id: str, background_tasks: BackgroundTasks):
    """Trigger video generation process"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if not job.get("audio_path"):
        raise HTTPException(status_code=400, detail="No audio file uploaded")
    
    if not job.get("video_paths"):
        raise HTTPException(status_code=400, detail="No video files uploaded")
    
    # Start background processing
    background_tasks.add_task(process_video_generation, job_id)
    
    return {"job_id": job_id, "status": "processing_started"}


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Check processing status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "progress": job.get("progress", 0),
        "error": job.get("error"),
        "output_ready": job.get("status") == "completed"
    }


@app.get("/api/download/{job_id}")
async def download_video(job_id: str):
    """Download the generated video"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Video not ready")
    
    output_path = job.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"synced_video_{job_id}.mp4"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
