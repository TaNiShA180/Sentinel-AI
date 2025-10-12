import asyncio
import time
import requests # NEW: Import requests for location fetching
from datetime import datetime
# These modules will be created in the next steps.
# They contain the logic for interacting with OpenAI and alert services.
import ai_services
import alerting

# --- Configuration ---
THREAT_SCORE_THRESHOLD = 7 # Trigger alert if GPT-4V score is above this (e.g., 7 out of 10)
ALERT_KEYWORDS = ["help", "stop", "get away", "danger", "assault", "kidnap"]

def get_location_info():
    """
    Gets the approximate location based on the public IP address using ipinfo.io.
    """
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        # Format a user-friendly location string
        city = data.get("city", "Unknown City")
        region = data.get("region", "Unknown Region")
        country = data.get("country", "Unknown Country")
        loc = data.get("loc", "N/A") # Lat/Long
        return f"{city}, {region}, {country} (approx. coordinates: {loc})"
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not fetch location: {e}")
        return "Location could not be determined."
    
async def run_analysis(video_path: str, audio_path: str | None):
    """
    Orchestrates the analysis of video and audio files concurrently.
    """
    print("\n--- [Decision Engine] ---")
    print(f"🧠 Analysis started for video: {video_path}")
    if audio_path:
        print(f"🎵 With audio: {audio_path}")

    # --- 1. Concurrent API Calls ---
    # Prepare the tasks to be run at the same time.
    video_analysis_task = ai_services.analyze_video_with_gpt4v(video_path)
    
    if audio_path:
        audio_analysis_task = ai_services.transcribe_audio_with_whisper(audio_path)
        # Use asyncio.gather to run both tasks concurrently
        results = await asyncio.gather(video_analysis_task, audio_analysis_task)
        vision_result, audio_result = results
    else:
        # If there's no audio, just run the video analysis
        vision_result = await video_analysis_task
        audio_result = "" # No transcription available
        
    print(f"\n[AI Service Results]")
    print(f"Vision Analysis: {vision_result}")
    print(f"Audio Transcription: '{audio_result}'")

    # --- 2. Threat Assessment ---
    threat_detected = False
    threat_reason = ""

    # Check threat level from video analysis
    # Note: Assumes vision_result is a dict like {'threat_level': 8, 'description': '...'}
    try:
        if vision_result and vision_result.get("threat_level", 0) > THREAT_SCORE_THRESHOLD:
            threat_detected = True
            threat_reason = f"High threat score ({vision_result['threat_level']}) detected. Description: {vision_result.get('description', 'N/A')}"
    except (TypeError, AttributeError):
        print("⚠️ Warning: Could not parse vision result. It might not be a valid dictionary.")


    # Check for keywords in audio transcription, but only if a threat hasn't already been confirmed
    if not threat_detected and audio_result:
        transcription_lower = audio_result.lower()
        for keyword in ALERT_KEYWORDS:
            if keyword in transcription_lower:
                threat_detected = True
                threat_reason = f"Alert keyword ('{keyword}') detected in audio."
                break # Stop checking after the first keyword is found

    # --- 3. Trigger Actions ---
    if threat_detected:
        print(f"\n🚨🚨🚨 THREAT DETECTED! Reason: {threat_reason} 🚨🚨🚨")
        event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        event_location = get_location_info()
        print(f"📍 Location: {event_location}")
        print(f"🕒 Timestamp: {event_time}")
        
        # A. Generate a clear alert message for authorities
        event_description = vision_result.get('description', 'A potential threat was detected.')
        
        # CORRECTED: Pass the location and timestamp to the alert generation function.
        alert_message = await ai_services.generate_alert_message(
            event_description=event_description,
            location=event_location,
            timestamp=event_time
        )
        
        print(f"📝 Generated Alert Message: \"{alert_message}\"")

        # B. Dispatch alerts
        print("Dispatching alerts via SMS and Email...")
        
        # CORRECTED: Pass the timestamp and location to the SMS alert function.
        alerting.send_sms_alert(
            message=alert_message,
            timestamp=event_time,
            location=event_location
        )
        
        # CORRECTED: Pass the timestamp and location to the email alert function.
        alerting.send_email_alert(
            message=alert_message,
            video_path=video_path,
            timestamp=event_time,
            location=event_location
        )

    else:
        print("\n✅ No significant threat detected based on current rules.")

    print("--- [Decision Engine] Analysis complete. ---\n")


# Placeholder for direct testing if needed in the future
if __name__ == '__main__':
    # This block allows for testing the engine directly, e.g.,
    # asyncio.run(run_analysis("path/to/video.mp4", "path/to/audio.mp3"))
    print("This module is intended to be called by main.py")