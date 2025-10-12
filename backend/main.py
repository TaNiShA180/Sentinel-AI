import uvicorn
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
import os
import shutil
from moviepy import VideoFileClip
import time 
from datetime import datetime
# We will create the decision_engine module in the next step.
# For now, this import assumes it exists with a 'run_analysis' function.
import decision_engine

# --- App Setup ---
app = FastAPI(title="Sentinel AI Backend")

# Create a directory for temporary file storage
EVIDENCE_DIR = "evidence"
TEMP_DIR = "temp_files"
os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Background Tasks ---
def cleanup_files(file_paths: list):
    """
    A background task to safely delete temporary files after they are processed.
    """
    print("🧹 Starting cleanup task...")
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
                print(f"   - Removed temporary file: {path}")
            except OSError as e:
                print(f"   - Error removing file {path}: {e}")
    print("✅ Cleanup finished.")


# --- API Endpoints ---
@app.post("/analyze")
async def analyze_video_clip(background_tasks: BackgroundTasks, video_file: UploadFile = File(...)):
    """
    This endpoint receives a video clip, extracts its audio, and passes both
    to the decision engine for threat analysis in a background task.
    """
    # 1. Save the uploaded video to a temporary file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    evidence_video_path = os.path.join(EVIDENCE_DIR, f"{timestamp}_{video_file.filename}")
    
    try:
        with open(evidence_video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        print(f"📹 Evidence video saved to: {evidence_video_path}")
    except Exception as e:
        return {"status": "error", "message": f"Failed to save video file: {e}"}

    # 2. Extract the audio track
    temp_audio_path = None
    try:
        with VideoFileClip(evidence_video_path) as video_clip:
            if video_clip.audio:
                # Keep audio temporary, as it's only used for transcription
                base, _ = os.path.splitext(os.path.basename(evidence_video_path))
                temp_audio_path = os.path.join(TEMP_DIR, f"{base}.mp3")
                video_clip.audio.write_audiofile(temp_audio_path, logger=None)
                print(f"🎤 Audio extracted and saved temporarily to: {temp_audio_path}")
            else:
                print("🔇 No audio track found in the video.")
    except Exception as e:
        print(f"⚠️ Warning: Could not extract audio. Error: {e}")

    # 3. Call the Decision Engine as a background task
    # This allows us to return a response immediately without waiting for AI analysis.
    background_tasks.add_task(
        decision_engine.run_analysis,
        video_path=evidence_video_path,
        audio_path=temp_audio_path
    )

    # 4. Schedule the cleanup task to run after the analysis
    background_tasks.add_task(cleanup_files, file_paths=[ temp_audio_path])

    # 5. Return an immediate confirmation response
    print(f"✅ Analysis for '{video_file.filename}' has been started in the background.")
    return {
        "status": "analysis_started",
        "filename": video_file.filename,
        "evidence_path": evidence_video_path,
        "audio_found": temp_audio_path is not None
    }


@app.get("/")
def read_root():
    """A simple root endpoint to confirm the server is running."""
    return {"message": "Sentinel AI Backend is active. Send clips to /analyze."}


# This block allows you to run the server directly with the command 'python main.py'
if __name__ == "__main__":
    print("🚀 Starting Sentinel AI FastAPI server...")
    # reload=True will automatically restart the server when you save changes
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)