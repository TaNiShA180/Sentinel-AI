
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/8f0fd74a-f2dd-4a67-a011-915a45027f66" />


![Image](https://github.com/user-attachments/assets/e1fd883f-b2c5-4417-a267-70a1ab908e35)


https://github.com/user-attachments/assets/28bcfea5-fff9-4af0-8d80-2b8e26fb96c4



🚨 Sentinel AI: Proactive Threat Detection System
Sentinel AI is a proof-of-concept security system that leverages computer vision and generative AI to proactively detect potential public safety threats from a video feed. It captures motion-activated video clips, analyzes them in near real-time for signs of distress or assault, and automatically dispatches alerts to designated contacts via SMS and email.

🧠 Features
🎥 Motion-Activated Recording – The simulator.py script monitors a webcam or video file and intelligently records only when significant motion is detected.

🕒 Pre-Event Buffer – Captures several seconds of footage before the motion trigger to ensure full context.

⚡ Asynchronous AI Backend – A FastAPI server processes video clips in the background, enabling non-blocking real-time response.

🤖 AI-Powered Threat Analysis – Uses the Google Gemini Pro Vision model (gemini-2.5-pro) to detect distress or assault scenarios.

📱 Multi-Modal Alerting – Sends real-time alerts via Twilio (SMS) and SendGrid (Email) if a credible threat is detected.

🧩 Context-Rich Alerts – Alerts include a summary, timestamp, location, and video evidence attachment.

🧹 Automatic File Management – Temporary media files are cleaned up post-analysis to save space.

⚙️ How It Works
1. Capture (Client-Side)
simulator.py monitors the live or recorded feed for motion.

On detection, it packages a clip containing frames before and after the event.

2. Transmission
The clip is sent via HTTP POST to the FastAPI backend (main.py).

3. Ingestion (Server-Side)
The backend saves the video and queues analysis as a background task to maintain responsiveness.

4. AI Analysis
ai_services.py extracts keyframes.

Frames are sent to Google Gemini API for analysis.

The AI responds with structured JSON like:

json
Copy code
{
  "threat_level": 8,
  "description": "A person appears to be assaulted in a public area."
}
5. Decision & Alerting
decision_engine.py evaluates the AI response.

If threat_level exceeds the THREAT_SCORE_THRESHOLD, alerts are generated.

alerting.py dispatches SMS and email alerts using Twilio and SendGrid.

6. Cleanup
Temporary files are deleted after processing.

🧩 Project Structure
bash
Copy code
.
├── .env.example          # Example environment configuration
├── .gitignore
├── ai_services.py        # Handles Google Gemini API interactions
├── alerting.py           # Sends SMS (Twilio) & Email (SendGrid) alerts
├── decision_engine.py    # Core analysis and alert logic
├── main.py               # FastAPI backend server
├── requirement.txt       # Python dependencies
├── simulator.py          # Motion-detecting client simulator
└── test_videos/
    └── kidnapping-simulation.mp4
🧰 Prerequisites
Python 3.8+

Webcam or access to a video file

API keys for:

Google AI Studio (Gemini API)

Twilio (SMS alerts)

SendGrid (Email alerts)

🚀 Installation & Setup
1️⃣ Clone the Repository
bash
Copy code
git clone <your-repo-url>
cd <your-repo-directory>
2️⃣ Create a Virtual Environment
bash
Copy code
python -m venv venv
# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirement.txt
4️⃣ Set Up Environment Variables
Create a .env file in the root directory (based on .env.example):

bash
Copy code
cp .env.example .env
Then, edit it with your actual credentials:

bash
Copy code
# --- Google Gemini API ---
GOOGLE_API_KEY="YOUR_GOOGLE_AI_STUDIO_API_KEY"

# --- Twilio for SMS Alerts ---
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER="+15551234567"
RECIPIENT_PHONE_NUMBER="+15557654321"

# --- SendGrid for Email Alerts ---
SENDGRID_API_KEY="SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
FROM_EMAIL="alerts@yourdomain.com"
TO_EMAIL="recipient@example.com"
▶️ Running the System
1. Start the Backend Server
bash
Copy code
python main.py
Server will start at: http://0.0.0.0:8000

2. Run the Simulator
bash
Copy code
python simulator.py
Displays the live or test video feed.

When motion is detected, a clip is saved and sent for AI analysis.

🧠 Configuration Options
File	Parameter	Description
simulator.py	VIDEO_SOURCE	0 = webcam, or path to video file
MOTION_THRESHOLD	Motion sensitivity (lower = more sensitive)
PRE_MOTION_BUFFER_SECONDS	Seconds recorded before trigger
POST_MOTION_RECORD_SECONDS	Seconds recorded after trigger
decision_engine.py	THREAT_SCORE_THRESHOLD	Score required to trigger alerts
ALERT_KEYWORDS	Keywords for audio-based detection

📦 Dependencies
fastapi, uvicorn – Backend web server

google-generativeai – Gemini API integration

opencv-python – Video processing and motion detection

moviepy – Audio extraction from videos

twilio – SMS alerts

sendgrid – Email alerts

requests – Location & HTTP communication

python-dotenv – Environment variable management

📸 Example Workflow
Motion detected in camera feed.

Clip is recorded and sent to server.

Gemini AI analyzes frames for distress patterns.

If threat detected → SMS & email alert dispatched.

Temporary files deleted automatically.

🧾 License
This project is released for educational and research purposes only.
Unauthorized use for surveillance or privacy invasion is strictly prohibited.

👩‍💻 Author
Tanisha Vasudeva
🌐 AI & ML Developer | Computer Vision Enthusiast
