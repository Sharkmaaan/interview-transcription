#!/usr/bin/env python3

import os
import subprocess
import glob
from datetime import datetime
from openai import OpenAI

# Read API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) #Replace key here with own API

INPUT_DIR = #Put path to where the MP4's will be here
OUTPUT_DIR = #Put path to where MP3's should go
TRANSCRIPT_DIR = #Put path to where transcripts should go
LOG_FILE = #Put path to where logs should go

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def log(message):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now()}: {message}\n")
    print(message)

# Find all MP4 files
mp4_files = glob.glob(os.path.join(INPUT_DIR, "*.mp4"))

for mp4_file in mp4_files:
    filename = os.path.basename(mp4_file)
    name = os.path.splitext(filename)[0]
    mp3_file = os.path.join(OUTPUT_DIR, f"{name}.mp3")
    
    log(f"Converting {filename}")
    
    # Convert to MP3
    try:
        subprocess.run([
            "/opt/homebrew/bin/ffmpeg", "-i", mp4_file,
            "-vn", "-acodec", "libmp3lame", "-b:a", "32k",
            mp3_file
        ], check=True, capture_output=True)
        
        log(f"Success - {name}.mp3 created")
        
        # Transcribe using API
        log(f"Starting API transcription of {name}.mp3")
        
        with open(mp3_file, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Save transcript
        transcript_file = os.path.join(TRANSCRIPT_DIR, f"{name}.txt")
        with open(transcript_file, 'w') as f:
            f.write(transcript)
        
        log(f"Transcription complete for {name}")
        
        # Delete original
        os.remove(mp4_file)
        log(f"Deleted {filename}")
        
    except Exception as e:
        log(f"Failed to process {filename}: {e}")