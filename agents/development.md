# Development Plan: Beat-Synced Video Generator

This document outlines the phased development process for building the intelligent video segmentation and assembly product.

## System Architecture

### 1. High-Level Design
The system follows a layered architecture to separate concerns between the user interface, API handling, and core processing logic.

- **Presentation Layer (Frontend)**: 
    - Single Page Application (HTML/JS/TailwindCSS).
    - Communicates with the Backend via REST API.
    - Responsible for file uploads, progress polling, and video playback.
- **Application Layer (API)**:
    - Built with **FastAPI**.
    - Orchestrates the workflow: Upload -> Trigger Job -> Poll Status -> Serve Result.
    - Manages background tasks for long-running video processing.
- **Service Layer (Core Logic)**:
    - **AudioService**: Uses `librosa` for beat tracking and tempo estimation.
    - **VideoService**: Uses `PySceneDetect` for segmentation and `OpenCV` for motion analysis.
    - **AssemblyService**: Uses `MoviePy` to combine assets based on sync data.
- **Data/Storage Layer**:
    - **Temp Storage**: Local file system integration for processing raw assets.
    - **Job State**: In-memory (or simple JSON file) tracking of job status (Queued, Processing, Completed, Failed).

### 2. Data Flow
1. **Input**: User uploads N raw videos + 1 music track.
2. **Processing**:
   - `AudioService` extracts beat timestamps.
   - `VideoService` segments raw videos and scores them.
   - `AssemblyService` matches beats to best segments and renders.
3. **Output**: Final MP4 file served back to the user.

---


## Phase 1: Environment Setup & Dependencies
- [ ] **Dependency Management**
    - [ ] Update `requirements.txt` with necessary libraries:
        - `librosa` (Audio analysis)
        - `moviepy` (Video editing)
        - `scenedetect[opencv]` (Scene detection)
        - `opencv-python` (Computer vision/Motion analysis)
        - `numpy` (Data handling)
    - [ ] Create a setup script or verify FFmpeg installation (Crucial for MoviePy).
- [ ] **Project Structure**
    - [ ] Create `services/` directory for core logic modules.
    - [ ] Create `temp/` directory for file processing.

## Phase 2: Audio Analysis Module
- [ ] **Beat Detection Implementation** (`services/audio.py`)
    - [ ] Implement `extract_beat_timestamps(audio_path)` using `librosa`.
    - [ ] Return data structure: List of beat timestamps and estimated tempo.
    - [ ] Create a utility to save/load beat data as JSON.
- [ ] **Verification**
    - [ ] Unit test: Run on a sample audio file and verify timestamp output.

## Phase 3: Video Analysis Module
- [ ] **Scene Detection** (`services/video.py`)
    - [ ] Implement `detect_scenes(video_path)` using `PySceneDetect`.
    - [ ] Configure `ContentDetector` sensitivity.
- [ ] **Motion Analysis** (`services/video.py`)
    - [ ] Implement `calculate_motion_intensity(video_path, start_frame, end_frame)` using OpenCV Optical Flow.
    - [ ] Create a scoring function `score_scene(motion, duration_match, visual_quality)`.
- [ ] **Segment Selection**
    - [ ] Implement `select_best_segments(scenes, beat_durations)` algorithm.
    - [ ] Logic to match best scene duration to beat interval.

## Phase 4: Assembly & Generation
- [ ] **Video Assembly** (`services/assembly.py`)
    - [ ] Implement `assemble_video(selected_segments, audio_path)`.
    - [ ] Use `MoviePy` to cut clips and concatenate them.
    - [ ] Overlay the original audio track.
    - [ ] Export final result to MP4.
- [ ] **Integration Test**
    - [ ] Run the full pipeline manually: Input Audio + Video -> Output Video.

## Phase 5: API & Productization
- [ ] **API Endpoints** (`main.py`)
    - [ ] `POST /upload/audio`: Handle audio file upload.
    - [ ] `POST /upload/video`: Handle raw video upload.
    - [ ] `POST /generate`: Trigger the generation process.
    - [ ] `GET /status/{job_id}`: Check processing status.
- [ ] **Frontend Integration (Optional/Later)**
    - [ ] Connect basic UI to these endpoints.

## Phase 6: User Interface (UI)
- [ ] **Frontend Development** (`public/index.html`, `public/script.js`, `public/style.css`)
    - [ ] **Design**: Clean, Minimalist "Shadcn-like" aesthetic (Grayscale, refined typography).
    - [ ] **Tech Stack**: HTML, JavaScript, TailwindCSS (via CDN).
    - [ ] **Components**:
        - [ ] Drag & Drop File Upload Area (Audio & Video).
        - [ ] "Generate Sync" Primary Button.
        - [ ] Progress Steps (Analyzing -> Detecting -> Assembling).
        - [ ] Video Player with minimal controls.
    - [ ] **Interaction**: Vanilla JS to fetch from API endpoints.

