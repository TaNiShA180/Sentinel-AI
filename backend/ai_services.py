# ai_services.py

import os
import cv2
import json
from dotenv import load_dotenv
from PIL import Image, PngImagePlugin
import google.generativeai as genai

# --- Configuration & API Key Setup ---
load_dotenv()

# Configure the Google Gemini client
try:
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file. Please add it.")
    genai.configure(api_key=google_api_key)
except Exception as e:
    print(f"⚠️ Error configuring Google Gemini: {e}")

# --- Main Service Functions ---

async def analyze_video_with_gpt4v(video_path: str, frames_to_extract: int = 10) -> dict | None:
    """
    Analyzes a video using the Gemini 1.5 Flash model.
    """
    print(f"   [AI Service] Starting Gemini analysis for {video_path}...")
    
    # 1. Extract video frames as PIL.Image objects
    pil_images = []
    try:
        video = cv2.VideoCapture(video_path)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = [int(i * total_frames / frames_to_extract) for i in range(frames_to_extract)]

        for i in frame_indices:
            video.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, frame = video.read()
            if not success:
                continue
            # Convert frame from BGR (OpenCV) to RGB (PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_images.append(Image.fromarray(frame_rgb))
        
        video.release()
        
        if not pil_images:
            print("   - Error: Could not extract any frames from the video.")
            return None
            
        print(f"   - Extracted {len(pil_images)} frames for analysis.")

    except Exception as e:
        print(f"   - Error processing video file: {e}")
        return None

    # 2. Prepare the request for Gemini
    # Use the vision-capable model
    model = genai.GenerativeModel(model_name="gemini-2.5-pro")
    
    prompt = """
    Analyze this sequence of video frames for a public safety threat.
    Is a person showing clear signs of distress, struggling against another person,
    being forcibly moved, or being abducted?
    Respond ONLY in JSON format with two keys:
    1. 'threat_level': An integer from 1 to 10, where 1 is no threat and 10 is a definite, severe assault or abduction.
    2. 'description': A brief, 20-word summary of the action.
    Example response: {"threat_level": 8, "description": "A person is being forcibly dragged by another individual towards a vehicle against their will."}
    """
    
    # The request must contain the prompt first, then all the images
    request_contents = [prompt] + pil_images
    
    # 3. Send the request to Google
    try:
        response = await model.generate_content_async(request_contents)
        # Clean up the response text to ensure it's valid JSON
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        return json.loads(response_text)

    except Exception as e:
        print(f"   - An unexpected error occurred during API call: {e}")
    
    return None


async def transcribe_audio_with_whisper(audio_path: str) -> str:
    """
    NOTE: The Google Gemini API does not have an audio transcription feature like Whisper.
    This function will be skipped and will return an empty string.
    """
    print("   [AI Service] Audio transcription skipped: Gemini API does not support this feature.")
    return ""


async def generate_alert_message(event_description: str, location: str, timestamp: str) -> str:
    """
    Generates a concise, human-readable alert message using the Gemini text model,
    including location and time context.
    """
    print("   [AI Service] Generating formatted alert message with location and time...")
    
    model = genai.GenerativeModel(model_name="gemini-2.5-pro")
    
    # MODIFICATION: The prompt now includes the location and timestamp
    # This gives the AI context to generate a more complete alert.
    prompt = f"""
    You are a public safety alert system. Based on the following event details, generate a clear,
    concise emergency alert message suitable for law enforcement. Be direct and professional.
    **Crucially, the entire message must be under 450 characters to fit within 3 SMS segments.**

    Event Time: {timestamp}
    Event Location: {location}
    Event Description: "{event_description}"

    Generated Alert:
    """
    
    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"   - An unexpected error occurred during alert generation: {e}")
        # MODIFICATION: The fallback message now also includes the new data.
        return f"EMERGENCY ALERT: High-threat event detected at {location} on {timestamp}. Description: {event_description}"