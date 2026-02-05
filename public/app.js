// App state
let jobId = null;
let audioFile = null;
let videoFiles = [];
let statusCheckInterval = null;

// DOM elements
const uploadSection = document.getElementById('upload-section');
const processingSection = document.getElementById('processing-section');
const resultSection = document.getElementById('result-section');

const audioUploadZone = document.getElementById('audio-upload-zone');
const audioInput = document.getElementById('audio-input');
const audioFileInfo = document.getElementById('audio-file-info');
const audioFilename = document.getElementById('audio-filename');
const removeAudioBtn = document.getElementById('remove-audio');

const videoUploadZone = document.getElementById('video-upload-zone');
const videoInput = document.getElementById('video-input');
const videoFilesList = document.getElementById('video-files-list');

const generateBtn = document.getElementById('generate-btn');
const statusText = document.getElementById('status-text');
const statusDetail = document.getElementById('status-detail');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');

const resultVideo = document.getElementById('result-video');
const resultVideoSource = document.getElementById('result-video-source');
const downloadBtn = document.getElementById('download-btn');
const newVideoBtn = document.getElementById('new-video-btn');

// Audio upload handlers
audioUploadZone.addEventListener('click', () => audioInput.click());
audioUploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    audioUploadZone.classList.add('dragover');
});
audioUploadZone.addEventListener('dragleave', () => {
    audioUploadZone.classList.remove('dragover');
});
audioUploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    audioUploadZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleAudioFile(files[0]);
    }
});
audioInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleAudioFile(e.target.files[0]);
    }
});
removeAudioBtn.addEventListener('click', () => {
    audioFile = null;
    audioFileInfo.classList.add('hidden');
    audioUploadZone.classList.remove('hidden');
    updateGenerateButton();
});

// Video upload handlers
videoUploadZone.addEventListener('click', () => videoInput.click());
videoUploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    videoUploadZone.classList.add('dragover');
});
videoUploadZone.addEventListener('dragleave', () => {
    videoUploadZone.classList.remove('dragover');
});
videoUploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    videoUploadZone.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    handleVideoFiles(files);
});
videoInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    handleVideoFiles(files);
});

// Generate button
generateBtn.addEventListener('click', startGeneration);

// Download and new video buttons
downloadBtn.addEventListener('click', downloadVideo);
newVideoBtn.addEventListener('click', resetApp);

// Handle audio file upload
async function handleAudioFile(file) {
    if (!file.type.match('audio.*')) {
        alert('Please select a valid audio file');
        return;
    }
    
    audioFile = file;
    audioFilename.textContent = file.name;
    audioFileInfo.classList.remove('hidden');
    audioUploadZone.classList.add('hidden');
    
    // Upload to server
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload/audio', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Upload failed');
        
        const data = await response.json();
        jobId = data.job_id;
        console.log('Audio uploaded, job ID:', jobId);
        
        updateGenerateButton();
    } catch (error) {
        console.error('Error uploading audio:', error);
        alert('Failed to upload audio file');
        audioFile = null;
        audioFileInfo.classList.add('hidden');
        audioUploadZone.classList.remove('hidden');
    }
}

// Handle video files upload
async function handleVideoFiles(files) {
    const validFiles = files.filter(f => f.type.match('video.*'));
    
    if (validFiles.length === 0) {
        alert('Please select valid video files');
        return;
    }
    
    for (const file of validFiles) {
        videoFiles.push(file);
        addVideoToList(file);
        
        // Upload to server
        if (jobId) {
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch(`/api/upload/video/${jobId}`, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) throw new Error('Upload failed');
                
                console.log('Video uploaded:', file.name);
            } catch (error) {
                console.error('Error uploading video:', error);
                alert(`Failed to upload ${file.name}`);
            }
        }
    }
    
    updateGenerateButton();
}

// Add video to list UI
function addVideoToList(file) {
    const videoItem = document.createElement('div');
    videoItem.className = 'flex items-center justify-between bg-gray-50 rounded-lg p-3';
    videoItem.innerHTML = `
        <div class="flex items-center space-x-3">
            <svg class="h-5 w-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z"></path>
            </svg>
            <span class="text-sm font-medium text-gray-700">${file.name}</span>
        </div>
        <button class="remove-video text-red-600 hover:text-red-700" data-filename="${file.name}">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;
    
    videoItem.querySelector('.remove-video').addEventListener('click', () => {
        removeVideo(file.name);
        videoItem.remove();
    });
    
    videoFilesList.appendChild(videoItem);
}

// Remove video from list
function removeVideo(filename) {
    videoFiles = videoFiles.filter(f => f.name !== filename);
    updateGenerateButton();
}

// Update generate button state
function updateGenerateButton() {
    generateBtn.disabled = !(audioFile && videoFiles.length > 0);
}

// Start generation process
async function startGeneration() {
    if (!jobId) {
        alert('Please upload files first');
        return;
    }
    
    try {
        const response = await fetch(`/api/generate/${jobId}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Generation failed');
        
        showProcessing();
        startStatusPolling();
    } catch (error) {
        console.error('Error starting generation:', error);
        alert('Failed to start video generation');
    }
}

// Show processing screen
function showProcessing() {
    uploadSection.classList.add('hidden');
    processingSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
}

// Start polling for status updates
function startStatusPolling() {
    statusCheckInterval = setInterval(checkStatus, 2000);
}

// Check processing status
async function checkStatus() {
    try {
        const response = await fetch(`/api/status/${jobId}`);
        
        if (!response.ok) throw new Error('Status check failed');
        
        const data = await response.json();
        updateProgress(data);
        
        if (data.status === 'completed') {
            clearInterval(statusCheckInterval);
            showResult();
        } else if (data.status === 'failed') {
            clearInterval(statusCheckInterval);
            alert('Video generation failed: ' + (data.error || 'Unknown error'));
            resetApp();
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Update progress UI
function updateProgress(data) {
    const progress = data.progress || 0;
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `${progress}%`;
    
    // Update status text
    const statusMessages = {
        'processing': 'Processing your files...',
        'analyzing_audio': 'Analyzing music beats...',
        'detecting_scenes': 'Detecting video scenes...',
        'selecting_segments': 'Selecting best segments...',
        'assembling_video': 'Assembling final video...'
    };
    
    statusText.textContent = statusMessages[data.status] || 'Processing...';
    
    // Update progress steps
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach(step => {
        step.classList.remove('active');
    });
    
    if (progress < 50) {
        steps[0]?.classList.add('active');
    } else if (progress < 80) {
        steps[0]?.classList.add('active');
        steps[1]?.classList.add('active');
    } else {
        steps[0]?.classList.add('active');
        steps[1]?.classList.add('active');
        steps[2]?.classList.add('active');
    }
}

// Show result
function showResult() {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultSection.classList.remove('hidden');
    
    // Set video source
    resultVideoSource.src = `/api/download/${jobId}`;
    resultVideo.load();
}

// Download video
function downloadVideo() {
    window.open(`/api/download/${jobId}`, '_blank');
}

// Reset app
function resetApp() {
    jobId = null;
    audioFile = null;
    videoFiles = [];
    
    audioFileInfo.classList.add('hidden');
    audioUploadZone.classList.remove('hidden');
    videoFilesList.innerHTML = '';
    
    uploadSection.classList.remove('hidden');
    processingSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    
    updateGenerateButton();
    
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
}
