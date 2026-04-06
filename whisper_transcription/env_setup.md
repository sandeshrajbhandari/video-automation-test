  source /Users/sandeshrajbhandari/Documents/root_venv/bin/activate
    ```
- Start the server:
  ```bash
  cd /Users/sandeshrajbhandari/Documents/VID_REPOS/video-automation-test/whisper_transcription
  uvicorn api_server:app --host 0.0.0.0 --port 8000
  ```
- Test your client function against `http://localhost:8000/transcribe`.


 cd /Users/sandeshrajbhandari/Documents/VID_REPOS/video-automation-test/whisper_transcription
  uvicorn api_server:app --host 0.0.0.0 --port 8000