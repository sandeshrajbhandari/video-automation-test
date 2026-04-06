import os
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from transcribe_video import transcribe

app = FastAPI(title="Whisper Transcription API")


@app.post("/transcribe")
async def transcribe_endpoint(
    file: UploadFile = File(...),
    mode: Optional[str] = Form("both"),
):
    if file.content_type not in ("video/mp4", "audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp3", "audio/mp4", "audio/aac", "audio/ogg", "audio/webm", "video/quicktime", "video/x-matroska"):
        # Allow a variety of audio/video types, default to proceed anyway
        pass
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or "upload")[1] or ".mp4") as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read upload: {exc}")

    try:
        result = transcribe(temp_path, mode=mode or "both")
        return JSONResponse(content=result)
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass


