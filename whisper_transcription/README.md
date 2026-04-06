## Whisper Transcription API

Run a local API for video/audio transcription using faster-whisper.

### Setup

1. Ensure ffmpeg is installed and available on your PATH.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

The first run will download the Whisper model (size `base`) into `whisper_models/base`.

### Start the server

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### Endpoint

- `POST /transcribe`
  - form fields: `mode` = `sentence` | `sentence_from_words` | `both` | `word`
  - file field: `file` (video or audio)

### Example client call

```python
import json
import requests

def fetch_transcription(
    video_file_path: str,
    mode: str = "both",
    transcribe_url: str = "http://localhost:8000/transcribe",
    timeout_seconds: int = 120,
):
    with open(video_file_path, "rb") as fp:
        files = {"file": (video_file_path, fp, "video/mp4")}
        data = {"mode": mode}
        r = requests.post(transcribe_url, files=files, data=data, timeout=timeout_seconds)
    r.raise_for_status()
    return r.json()

resp = fetch_transcription("inputs/video_auto_test.mp4", mode="both")
print(json.dumps(resp, indent=2))
```

### CLI (optional)

You can still run the original CLI:

```bash
python transcribe_video.py --mode sentence --input inputs/video_auto_test.mp4
```


