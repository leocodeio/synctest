#!/usr/bin/env python
"""Verification script for Beat-Synced Video Generator setup"""

from pathlib import Path

# Check if all files exist
files = {
    'main.py': True,
    'public/index.html': True,
    'public/app.js': True,
    'services/__init__.py': True,
    'services/audio.py': True,
    'services/video.py': True,
    'services/assembly.py': True,
    'requirements.txt': True,
    'README.md': True
}

print('Project Structure Verification:')
print('-' * 40)
for file, _ in files.items():
    path = Path(file)
    exists = path.exists()
    status = '✓' if exists else '✗'
    print(f'{status} {file}')

# Check if public/index.html contains key HTML elements
with open('public/index.html', 'r') as f:
    html_content = f.read()
    
print('\nHTML Content Verification:')
print('-' * 40)
checks = {
    'Contains Beat-Synced Video Generator title': 'Beat-Synced Video Generator' in html_content,
    'Contains upload zones': 'upload-zone' in html_content,
    'Contains app.js reference': 'app.js' in html_content,
    'Contains TailwindCSS CDN': 'tailwindcss' in html_content,
}

for check, result in checks.items():
    status = '✓' if result else '✗'
    print(f'{status} {check}')

# Check if main.py has root route
with open('main.py', 'r') as f:
    main_content = f.read()
    
print('\nAPI Endpoints Verification:')
print('-' * 40)
endpoints = {
    'Root route (/)': '@app.get("/", response_class=HTMLResponse)' in main_content,
    'Upload audio': '/api/upload/audio' in main_content,
    'Upload video': '/api/upload/video' in main_content,
    'Generate video': '/api/generate' in main_content,
    'Status check': '/api/status' in main_content,
    'Download video': '/api/download' in main_content,
}

for endpoint, exists in endpoints.items():
    status = '✓' if exists else '✗'
    print(f'{status} {endpoint}')

print('\n' + '=' * 40)
print('Ready to install dependencies and run!')
print('=' * 40)
print('\nNext steps:')
print('1. Install FFmpeg (required for video processing)')
print('2. Run: pip install -r requirements.txt')
print('3. Run: python main.py')
print('4. Open: http://localhost:5001')
