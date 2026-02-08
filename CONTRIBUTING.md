# Contributing to Beat-Synced Video Generator

Thank you for your interest in contributing to this project! This guide will help you get started with setting up the development environment and running the application on your system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
  - [Linux (Fedora/RHEL)](#linux-fedorarhel)
- [Verifying Installation](#verifying-installation)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Submitting Contributions](#submitting-contributions)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.10 or higher**
- **FFmpeg** (required for video processing)
- **pip** (Python package manager)
- **Git** (for version control)

---

## Installation Guide

### Windows

#### Step 1: Install Python

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### Step 2: Install FFmpeg

**Option A: Using Chocolatey (Recommended)**
```cmd
# Install Chocolatey if not already installed
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg
```

**Option B: Manual Installation**
1. Download FFmpeg from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the archive to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add `C:\ffmpeg\bin`
   - Click OK on all windows

#### Step 3: Clone the Repository

```cmd
git clone <repository-url>
cd synctest
```

#### Step 4: Create Virtual Environment

```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate
```

#### Step 5: Install Python Dependencies

```cmd
pip install -r requirements.txt
```

---

### macOS

#### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Python

```bash
# Install Python 3
brew install python@3.11

# Verify installation
python3 --version
pip3 --version
```

#### Step 3: Install FFmpeg

```bash
brew install ffmpeg
```

#### Step 4: Clone the Repository

```bash
git clone <repository-url>
cd synctest
```

#### Step 5: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

#### Step 6: Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### Linux (Ubuntu/Debian)

#### Step 1: Update Package Lists

```bash
sudo apt update
```

#### Step 2: Install Python and pip

```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Verify installation
python3 --version
pip3 --version
```

#### Step 3: Install FFmpeg

```bash
sudo apt install ffmpeg -y
```

#### Step 4: Install Git (if not installed)

```bash
sudo apt install git -y
```

#### Step 5: Clone the Repository

```bash
git clone <repository-url>
cd synctest
```

#### Step 6: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

#### Step 7: Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### Linux (Fedora/RHEL)

#### Step 1: Update System

```bash
sudo dnf update -y
```

#### Step 2: Install Python and pip

```bash
# Install Python 3 and development tools
sudo dnf install python3 python3-pip python3-virtualenv -y

# Verify installation
python3 --version
pip3 --version
```

#### Step 3: Install FFmpeg

```bash
# Enable RPM Fusion repository
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm -y

# Install FFmpeg
sudo dnf install ffmpeg -y
```

#### Step 4: Install Git (if not installed)

```bash
sudo dnf install git -y
```

#### Step 5: Clone the Repository

```bash
git clone <repository-url>
cd synctest
```

#### Step 6: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

#### Step 7: Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Verifying Installation

After completing the installation steps, verify everything is set up correctly:

### 1. Verify FFmpeg

```bash
ffmpeg -version
```

You should see FFmpeg version information.

### 2. Verify Python Packages

```bash
python verify_setup.py
```

This script will check all required dependencies and report any issues.

### 3. Check Project Structure

Ensure the following directories exist:
```
synctest/
├── agents/
├── services/
├── public/
├── temp/
│   ├── uploads/
│   └── outputs/
├── main.py
├── requirements.txt
└── README.md
```

---

## Running the Application

### Development Server

1. **Activate virtual environment** (if not already activated):

   **Windows:**
   ```cmd
   .venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```bash
   source .venv/bin/activate
   ```

2. **Start the server:**

   ```bash
   python main.py
   ```

3. **Access the application:**

   Open your browser and navigate to: `http://localhost:5001`

### Using the Application

1. **Upload Music Track:**
   - Click the upload area or drag-and-drop an audio file
   - Supported formats: MP3, WAV, M4A, FLAC

2. **Upload Raw Videos:**
   - Upload 3-10 video files
   - Supported formats: MP4, MOV, AVI, MKV

3. **Generate Video:**
   - Click "Generate Synced Video"
   - Monitor real-time progress

4. **Download Result:**
   - Preview the generated video
   - Download when complete

### API Testing

You can test the API endpoints using `curl` or tools like Postman:

```bash
# Upload audio
curl -X POST -F "file=@music.mp3" http://localhost:5001/api/upload/audio

# Check status
curl http://localhost:5001/api/status/{job_id}
```

---

## Development Workflow

### Project Structure

```
synctest/
├── agents/              # Development documentation and references
├── services/           # Core processing modules
│   ├── audio.py       # Beat detection using librosa
│   ├── video.py       # Scene detection and motion analysis
│   └── assembly.py    # Video compilation using MoviePy
├── public/            # Frontend files
│   ├── index.html    # Main UI
│   └── app.js        # Frontend logic
├── temp/             # Temporary storage
│   ├── uploads/     # Uploaded files
│   └── outputs/     # Generated videos
└── main.py          # FastAPI application entry point
```

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** in the appropriate files

3. **Test your changes** thoroughly

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

---

## Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

**Example:**
```python
def extract_beat_timestamps(audio_path: str) -> dict:
    """
    Extract beat timestamps from an audio file.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        dict: Contains beat times, tempo, and intervals
    """
    # Implementation here
    pass
```

### JavaScript Code Style

- Use ES6+ features
- Use `const` and `let` instead of `var`
- Add comments for complex logic
- Keep functions small and focused

### File Naming

- Python files: `lowercase_with_underscores.py`
- JavaScript files: `camelCase.js`
- HTML files: `lowercase.html`

---

## Testing Guidelines

### Manual Testing

Before submitting changes:

1. **Test basic workflow:**
   - Upload audio file
   - Upload video files
   - Generate video
   - Download result

2. **Test error handling:**
   - Invalid file formats
   - Missing files
   - Network interruptions

3. **Test edge cases:**
   - Very short videos
   - Very long videos
   - Multiple music tracks

### Adding New Features

When adding new features:

1. Update documentation in relevant files
2. Test on at least two different operating systems if possible
3. Ensure backward compatibility
4. Update README.md if user-facing features change

---

## Submitting Contributions

### Pull Request Process

1. **Fork the repository** (if external contributor)

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit them with clear messages

4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request:**
   - Provide a clear title and description
   - Reference any related issues
   - Include screenshots/videos for UI changes

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear and descriptive

---

## Getting Help

If you encounter issues:

1. Check the [README.md](README.md) troubleshooting section
2. Review existing issues in the repository
3. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Your OS and Python version
   - Error messages (if any)

---

## Common Issues and Solutions

### "FFmpeg not found"
- Verify FFmpeg is installed: `ffmpeg -version`
- Ensure FFmpeg is in your system PATH
- Restart your terminal/command prompt

### "Module not found" errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### "Permission denied" errors
- On Linux/macOS, you may need to use `sudo` for system-wide installations
- Or use virtual environments (recommended)

### Port 5001 already in use
- Stop other applications using port 5001
- Or modify the port in `main.py`:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=5002)
  ```

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Beat-Synced Video Generator!
