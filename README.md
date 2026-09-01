# Pedro Pedro Webcam

A webcam app that uses real-time hand tracking to trigger the "Pedro Pedro" meme effect — when you press your palms together in front of the camera, the app masks your face into a circle, spins it, and punches in on the beat of the song, synced via automatic beat detection.

Built with **PyQt6**, **OpenCV**, and **MediaPipe Hands**.

## How it works

1. `main.py` launches a `QApplication` and opens the `Webcam` window.
2. `Webcam.py` grabs frames from your webcam, runs MediaPipe hand-landmark detection each frame, and classifies detected hands as left/right.
3. `pedro.py` (`Pedro` class) checks whether your hand landmarks are aligned in the "praying hands" pose. When they are:
   - It starts playing `PedroPedro.mp3`.
   - It masks the frame into a circular crop, continuously rotates it, and does a "zoom punch" (`dhukchuk`) on each detected beat.
   - When your hands separate, playback stops and the effect resets.
4. `beat.py` is a standalone helper script that uses `librosa` to analyze an MP3 and print its tempo and beat timestamps — this is how the hardcoded `beat_times` list in `pedro.py` was generated.

## Requirements

- Python 3.10+ (PyQt6 and mediapipe compatibility)
- A webcam
- The audio file `PedroPedro.mp3` in the project root

Install dependencies:

```bash
pip install -r requirements.txt
```

## Project structure

```
.
├── main.py           # Entry point — launches the PyQt app
├── Webcam.py          # Webcam capture, hand detection, frame pipeline
├── pedro.py           # Pedro effect logic: gesture check, mask/rotate/zoom, audio sync
├── beat.py            # Utility script to extract tempo/beat times from an audio file
├── requirements.txt    # Python dependencies
└── PedroPedro.mp3      # Audio track played during the effect
```

## Usage

Make sure `PedroPedro.mp3` is in the same directory as the scripts, then run:

```bash
python main.py
```

A window titled **"Hands up 🔫"** will open showing your webcam feed with hand landmarks drawn on it. Bring both palms together in front of the camera (fingers aligned) to trigger the effect.

