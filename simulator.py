# simulator.py

import cv2
import requests
import time
import os
import collections
import numpy as np

# --- Configuration ---
# Set to 0 for webcam, or provide a path to a video file e.g., "test_videos/street.mp4"
VIDEO_SOURCE = "test_videos/kiddnapping-simulation.mp4"

# CHANGED: This URL must point to your locally running FastAPI server (main.py)
# The default is http://127.0.0.1:8000, and the endpoint is /analyze.
BACKEND_URL = "http://127.0.0.1:8000/analyze"

# Frame settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 20.0

# Motion detection settings
MOTION_THRESHOLD = 500  # Lower value means more sensitive to motion
BLUR_SIZE = (21, 21)
MIN_MOTION_FRAMES = 8 # Number of consecutive frames with motion to trigger a recording

# Recording settings
PRE_MOTION_BUFFER_SECONDS = 10  # How many seconds of video to keep before motion
POST_MOTION_RECORD_SECONDS = 5   # How many seconds to record after motion stops

def send_clip_to_backend(video_path):
    """Sends the captured video clip to the FastAPI backend."""
    # CHANGED: The print statement now shows the correct full URL.
    print(f"📡 Sending clip '{video_path}' to the backend server at {BACKEND_URL}...")
    try:
        with open(video_path, 'rb') as f:
            files = {'video_file': (os.path.basename(video_path), f, 'video/mp4')}
            # NOTE: The URL already includes the /analyze endpoint from the config above.
            response = requests.post(BACKEND_URL, files=files, timeout=60) # Increased timeout for analysis

            if response.status_code == 200:
                print(f"✅ Clip sent successfully. Server response: {response.json()}")
                print("🚨 DETERRENT ACTIVATED (Simulation)")
            else:
                print(f"❌ Error sending clip. Status: {response.status_code}, Response: {response.text}")

    except requests.exceptions.ConnectionError as e:
        print("❌ CRITICAL ERROR: Could not connect to the backend server.")
        print(f"   Ensure 'main.py' is running and you are using the correct URL. Details: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ An unexpected request error occurred: {e}")
    finally:
        # Clean up the temporary file sent by the simulator
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"🗑️ Temporary simulator clip '{video_path}' removed.")

# ... (The rest of the file run_simulator() remains unchanged) ...

def run_simulator():
    """Main function to run the camera feed simulator."""
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video source '{VIDEO_SOURCE}'.")
        return

    # Initialize frame buffer using deque for efficient appends and pops from both ends
    buffer_size = PRE_MOTION_BUFFER_SECONDS * int(FPS)
    frame_buffer = collections.deque(maxlen=buffer_size)

    avg_frame = None
    motion_counter = 0
    is_recording = False

    print("🚀 Camera simulator started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video stream.")
            break

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        # 1. Store current frame in buffer
        frame_buffer.append(frame.copy())

        # 2. Motion Detection Logic
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, BLUR_SIZE, 0)

        if avg_frame is None:
            avg_frame = gray.copy().astype("float")
            continue

        cv2.accumulateWeighted(gray, avg_frame, 0.5)
        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg_frame))
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        motion_sum = np.sum(thresh)

        motion_detected = False
        if motion_sum > MOTION_THRESHOLD:
            motion_counter += 1
            if motion_counter >= MIN_MOTION_FRAMES:
                motion_detected = True
        else:
            motion_counter = 0

        # 3. Trigger and Package Logic
        if motion_detected and not is_recording:
            is_recording = True
            print("\n🏃 Motion detected! Starting to record post-motion clip...")

            post_motion_frames_to_capture = POST_MOTION_RECORD_SECONDS * int(FPS)
            post_motion_frames = []

            for _ in range(post_motion_frames_to_capture):
                ret_rec, frame_rec = cap.read()
                if not ret_rec:
                    break
                frame_rec = cv2.resize(frame_rec, (FRAME_WIDTH, FRAME_HEIGHT))
                post_motion_frames.append(frame_rec)

            # Combine pre-motion buffer with post-motion frames
            full_clip_frames = list(frame_buffer) + post_motion_frames

            # Save the combined clip
            clip_filename = f"clip_{int(time.time())}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(clip_filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

            for f in full_clip_frames:
                out.write(f)

            out.release()
            print(f"📹 Clip saved as '{clip_filename}'.")

            # 4. Send to Backend
            send_clip_to_backend(clip_filename)

            # Reset state
            is_recording = False
            motion_counter = 0
            # Clear buffer to avoid immediate re-trigger on the same event
            frame_buffer.clear()

        # Display the live feed (optional)
        cv2.imshow("Live Feed", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Simulator stopped.")

if __name__ == "__main__":
    run_simulator()