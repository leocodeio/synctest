# Audio Processing

This file contains information related to audio handling for the beat‑synced video pipeline.

## Beat Detection
- Uses **librosa** to load audio files and detect beats.
- Function `extract_beat_timestamps` (see `development.md` Step 1) returns a JSON with tempo and beat timestamps.
- Dependencies: `librosa`, `numpy`.

## Recommended Settings
- Sample rate: 22 050 Hz (default for librosa).
- Use `librosa.beat.beat_track` for robust tempo estimation.
- Store results in `*.json` files for later video alignment.

## References
- [librosa.beat.beat_track documentation](https://librosa.org/doc/main/generated/librosa.beat.beat_track.html)
