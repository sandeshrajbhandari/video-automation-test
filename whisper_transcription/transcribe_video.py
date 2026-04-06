"""
Transcribe videos from inputs folder with word-level timestamps using faster-whisper.

Requirements:
    pip install faster-whisper ffmpeg-python
    # Also ensure ffmpeg is installed and in your PATH
"""

import json
import os
from faster_whisper.utils import download_model
from faster_whisper import WhisperModel
import sys
import argparse

# Updated paths for new folder structure
INPUT_VIDEO_PATH = "inputs/video_auto_test.mp4"
OUTPUT_JSON = "outputs/video_auto_test_transcript.json"
MODEL_DIR = "whisper_models/base"
MODEL_SIZE = "base"  # You can use "small", "medium", etc. for better accuracy

# Download model if not present
if not os.path.exists(MODEL_DIR):
    print(f"Model not found in {MODEL_DIR}, downloading...")
    download_model(MODEL_SIZE, output_dir=MODEL_DIR)

# Load model from local directory
model = WhisperModel(MODEL_DIR, device="auto", compute_type="auto")
import faster_whisper

# Transcribe with word-level timestamps
def transcribe_with_word_timestamps(video_path):
    segments, info = model.transcribe(video_path, word_timestamps=True)
    words = []
    for segment in segments:
        for word in segment.words:
            words.append({
                "word": word.word,
                "start": word.start,
                "end": word.end
            })
    return words

# Transcribe and get sentence-level segments
def transcribe_to_sentences(video_path):
    # The 'segments' object is an iterator that yields sentence-like chunks
    segments, info = model.transcribe(video_path, word_timestamps=False) # No need for word timestamps here

    sentence_list = []
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    print("Transcribing...")
    
    for segment in segments:
        sentence_list.append({
            'text': segment.text.strip(),
            'start': segment.start,
            'end': segment.end
        })
        # Optional: Print progress to the console
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}")

    return sentence_list

# Build sentence-like segments from word-level output
def sentences_from_words(words):
    sentence_list = []
    current_words = []
    sentence_start = None
    for w in words:
        text = (w.get("word") or "").strip()
        if text == "":
            continue
        if sentence_start is None:
            sentence_start = w.get("start")
        current_words.append(w)
        # Sentence boundary heuristics: end on punctuation or long gap
        is_boundary = False
        if any(text.endswith(p) for p in [".", "!", "?", "…"]):
            is_boundary = True
        else:
            if len(current_words) >= 30:
                is_boundary = True
        if is_boundary:
            sentence_text = " ".join(x.get("word", "").strip() for x in current_words).strip()
            sentence_end = current_words[-1].get("end")
            if sentence_text:
                sentence_list.append({
                    "text": sentence_text,
                    "start": sentence_start,
                    "end": sentence_end
                })
            current_words = []
            sentence_start = None
    if current_words:
        sentence_text = " ".join(x.get("word", "").strip() for x in current_words).strip()
        sentence_end = current_words[-1].get("end")
        if sentence_text:
            sentence_list.append({
                "text": sentence_text,
                "start": sentence_start,
                "end": sentence_end
            })
    return sentence_list

# Unified transcribe entrypoint used by the API
def transcribe(video_path, mode="both"):
    # Supported modes: "word", "sentence", "sentence_from_words", "both"
    mode = (mode or "both").lower()
    if mode == "word":
        word_list = transcribe_with_word_timestamps(video_path)
        return {"word_level": word_list}
    if mode == "sentence":
        sentences = transcribe_to_sentences(video_path)
        return {"sentence_level": sentences}
    if mode == "sentence_from_words":
        word_list = transcribe_with_word_timestamps(video_path)
        sentences = sentences_from_words(word_list)
        return {"sentence_level": sentences}
    # both (default)
    word_list = transcribe_with_word_timestamps(video_path)
    sentences = transcribe_to_sentences(video_path)
    return {"word_level": word_list, "sentence_level": sentences}

def main():
    parser = argparse.ArgumentParser(description="Transcribe video with word or sentence level timestamps.")
    parser.add_argument('--mode', choices=['word', 'sentence'], default='sentence', help='Transcription mode: word or sentence (default: sentence)')
    parser.add_argument('--input', type=str, default=INPUT_VIDEO_PATH, help='Path to input video file')
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs("outputs", exist_ok=True)

    print(f"Transcribing {args.input} in {args.mode} mode...")
    if args.mode == 'word':
        result = transcribe_with_word_timestamps(args.input)
        output_json = OUTPUT_JSON.replace('.json', '_word_level.json')
    else:
        result = transcribe_to_sentences(args.input)
        output_json = OUTPUT_JSON.replace('.json', '_sentence_level.json')

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Transcription saved to {output_json}")

if __name__ == "__main__":
    main() 