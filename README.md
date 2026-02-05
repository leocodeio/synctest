# Beat-Synced Video Generator

An intelligent video segmentation and assembly system that automatically creates synchronized videos from raw footage and music tracks using AI-powered beat detection and motion analysis.

## Features

- **Beat Detection**: Automatically analyzes music tracks to identify beats and tempo using librosa
- **Scene Detection**: Intelligently segments videos into scenes using PySceneDetect
- **Motion Analysis**: Calculates motion intensity using OpenCV optical flow
- **Smart Assembly**: Matches video segments to beat intervals for perfect synchronization
- **Modern UI**: Clean, intuitive interface built with TailwindCSS
- **Real-time Progress**: Live status updates during processing

## Architecture

The system uses a layered architecture:

- **Frontend**: HTML/JavaScript/TailwindCSS single-page application
- **API Layer**: FastAPI backend with REST endpoints
- **Service Layer**: 
  - `AudioService`: Beat tracking with librosa
  - `VideoService`: Scene detection with PySceneDetect and motion analysis with OpenCV
  - `AssemblyService`: Video compilation with MoviePy

## Prerequisites

- Python 3.8+
- FFmpeg (required for MoviePy)

### Installing FFmpeg

**Windows**:
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**macOS**:
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install ffmpeg
```

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

The requirements include:
- fastapi
- uvicorn
- python-multipart
- librosa
- moviepy
- scenedetect[opencv]
- opencv-python
- numpy
- aiofiles

3. **Verify FFmpeg installation**:
```bash
ffmpeg -version
```

## Usage

### Starting the Server

Run the development server:
```bash
python main.py
```

The server will start at `http://localhost:5001`

### Using the Web Interface

1. **Open your browser** and navigate to `http://localhost:5001`

2. **Upload Music Track**:
   - Click or drag-and-drop your audio file (MP3, WAV, M4A, FLAC)
   - The system will extract beat timestamps

3. **Upload Raw Videos**:
   - Click or drag-and-drop video files (MP4, MOV, AVI, MKV)
   - Multiple videos can be uploaded

4. **Generate**:
   - Click "Generate Synced Video"
   - Watch real-time progress as the system:
     - Analyzes audio beats
     - Detects video scenes
     - Calculates motion intensity
     - Selects best segments
     - Assembles final video

5. **Download**:
   - Preview the generated video
   - Download the final result

### API Endpoints

The system provides REST API endpoints:

- `POST /api/upload/audio` - Upload audio file
- `POST /api/upload/video/{job_id}` - Upload video files
- `POST /api/generate/{job_id}` - Start generation process
- `GET /api/status/{job_id}` - Check processing status
- `GET /api/download/{job_id}` - Download generated video

### Python API Usage

You can also use the services programmatically:

```python
from services.audio import AudioService
from services.video import VideoService
from services.assembly import AssemblyService

# Extract beats from audio
audio_service = AudioService()
beat_data = audio_service.extract_beat_timestamps("music.mp3")

# Detect and analyze video scenes
video_service = VideoService()
scenes = video_service.detect_scenes("raw_video.mp4")
analyzed_scenes = video_service.analyze_scenes_with_motion("raw_video.mp4", scenes)

# Select best segments
beat_intervals = audio_service.get_beat_intervals(beat_data)
segments = video_service.select_best_segments(analyzed_scenes, beat_intervals)

# Assemble final video
assembly_service = AssemblyService()
output = assembly_service.assemble_video(
    segments,
    ["raw_video.mp4"],
    "music.mp3",
    "output.mp4"
)
```

## Project Structure

```
synctest/
├── agents/                 # Development documentation
├── services/              # Core processing modules
│   ├── __init__.py
│   ├── audio.py          # Beat detection (librosa)
│   ├── video.py          # Scene detection & motion analysis
│   └── assembly.py       # Video compilation (MoviePy)
├── public/               # Frontend files
│   ├── index.html       # Main UI
│   ├── app.js          # Frontend logic
│   └── favicon.ico
├── temp/                # Temporary file storage
│   ├── uploads/        # Uploaded files
│   └── outputs/        # Generated videos
├── main.py             # FastAPI application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## How It Works

### 1. Audio Analysis
- Loads audio file with librosa
- Extracts beat timestamps using `beat_track()`
- Calculates tempo (BPM)
- Computes beat intervals

### 2. Video Segmentation
- Detects scenes using PySceneDetect's ContentDetector
- Analyzes motion intensity with OpenCV optical flow
- Scores scenes based on motion and duration

### 3. Segment Selection
- Matches video scenes to beat intervals
- Selects best segments based on:
  - Motion intensity (60% weight)
  - Duration match (40% weight)

### 4. Video Assembly
- Cuts selected video segments
- Adjusts timing to match beat intervals
- Concatenates clips
- Overlays audio track
- Exports final MP4

## Configuration

You can adjust detection parameters in the code:

**Scene Detection Sensitivity** (services/video.py):
```python
scenes = video_service.detect_scenes(video_path, threshold=27.0)
# Lower threshold = more sensitive (more scenes detected)
```

**Motion Analysis Settings** (services/video.py):
```python
# Adjust optical flow parameters in calculate_motion_intensity()
flow = cv2.calcOpticalFlowFarneback(
    prvs, next_frame, None,
    pyr_scale=0.5,    # Pyramid scale
    levels=3,         # Number of pyramid levels
    winsize=15,       # Averaging window size
    iterations=3,     # Number of iterations
    poly_n=5,         # Polynomial expansion degree
    poly_sigma=1.2,   # Gaussian standard deviation
    flags=0
)
```

## Troubleshooting

**"FFmpeg not found" error**:
- Ensure FFmpeg is installed and in your system PATH
- Restart terminal/command prompt after installation

**"Import could not be resolved" warnings**:
- These are IDE warnings - install dependencies with pip to resolve
- The application will run correctly with all dependencies installed

**Long processing times**:
- Processing time depends on video length and quality
- Higher resolution videos take longer to process
- Multiple videos increase processing time

**Memory issues**:
- Large videos may require significant RAM
- Consider splitting very long videos before processing

## Performance Tips

1. Use videos with consistent quality
2. Trim videos to relevant sections before uploading
3. Use compressed audio formats (MP3) for faster beat detection
4. Close other applications during processing

## Future Enhancements

- [ ] Database integration for job persistence
- [ ] User authentication
- [ ] Advanced scene scoring algorithms
- [ ] Custom transition effects
- [ ] Batch processing support
- [ ] Cloud storage integration
- [ ] GPU acceleration for video processing

## License

This project is for educational and personal use.

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [librosa](https://librosa.org/) - Audio analysis
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing
- [PySceneDetect](https://scenedetect.com/) - Scene detection
- [OpenCV](https://opencv.org/) - Computer vision
- [TailwindCSS](https://tailwindcss.com/) - UI styling

