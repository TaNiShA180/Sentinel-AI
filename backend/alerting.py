import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64 
from datetime import datetime
# --- Configuration & Client Initialization ---
load_dotenv()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

# SendGrid Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")

# Initialize clients
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    print(f"⚠️ Warning: Could not initialize Twilio client. Is it configured in .env? Error: {e}")
    twilio_client = None

try:
    sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
except Exception as e:
    print(f"⚠️ Warning: Could not initialize SendGrid client. Is it configured in .env? Error: {e}")
    sendgrid_client = None

# --- Alerting Functions ---

def send_sms_alert(message: str, timestamp: str, location: str):
    """
    Sends an SMS alert using the Twilio API.
    """
    if not all([twilio_client, TWILIO_PHONE_NUMBER, RECIPIENT_PHONE_NUMBER]):
        print("   [Alerting Service] SMS not sent: Twilio is not fully configured in .env file.")
        return
    full_message = f"[Sentinel AI Alert]\n{message}\n\nTime: {timestamp}\nLocation: {location}"
    print(f"[Alerting Service] Sending SMS to {RECIPIENT_PHONE_NUMBER}...")
    try:
        message_instance = twilio_client.messages.create(
            body=full_message,
            from_=TWILIO_PHONE_NUMBER,
            to=RECIPIENT_PHONE_NUMBER
        )
        print(f"      - SMS sent successfully! SID: {message_instance.sid}")
    except TwilioRestException as e:
        print(f"      - ❌ Twilio API Error: Failed to send SMS. Error: {e}")
    except Exception as e:
        print(f"      - ❌ An unexpected error occurred while sending SMS: {e}")


def send_email_alert(message: str, video_path: str, timestamp: str, location: str):
    """
    Sends an email alert with details using the SendGrid API.
    """
    if not all([sendgrid_client, FROM_EMAIL, TO_EMAIL]):
        print("   [Alerting Service] Email not sent: SendGrid is not fully configured in .env file.")
        return
        
    print(f"   [Alerting Service] Sending email to {TO_EMAIL}...")
    formatted_message = message.replace('\n', '<br>')
    # For local testing, we'll just include the file path in the body.
    # A production system would upload the video to cloud storage (e.g., S3)
    # and include a public link here.
    html_content = f"""
    <h3>Sentinel AI - High Priority Threat Alert</h3>
    <p>An automated threat detection system has identified a potential public safety incident.</p>
    
    <p><strong>Time of Event:</strong> {timestamp}</p>
    <p><strong>Approximate Location:</strong> {location}</p>

    <p><strong>Generated Alert Message:</strong></p>
    <blockquote style='border-left: 4px solid #cc0000; padding-left: 10px; margin-left: 5px;'>
      {formatted_message}
    </blockquote>
    <p>A video clip of the event is attached to this email for your review.</p>
    <p><strong>Original File Path:</strong> <code>{video_path}</code></p>
    <hr>
    <p><em>This is an automated message. Please review the evidence immediately.</em></p>
    """

    message_obj = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject="[CRITICAL] Sentinel AI - Automated Threat Alert",
        html_content=html_content
    )

    try:
        with open(video_path, 'rb') as f:
            video_data = f.read()
        
        # Encode the video data to base64
        encoded_file = base64.b64encode(video_data).decode()

        # Create the attachment object
        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName(os.path.basename(video_path)),
            FileType('video/mp4'),
            Disposition('attachment')
        )
        message_obj.attachment = attachedFile
        print(f"      - Attached video file: {video_path}")

    except FileNotFoundError:
        print(f"      - ❌ Attachment Error: Video file not found at {video_path}. Email will be sent without it.")
    except Exception as e:
        print(f"      - ❌ An unexpected error occurred while attaching the file: {e}")
    # --- End of new attachment logic ---

    try:
        response = sendgrid_client.send(message_obj)
        if 200 <= response.status_code < 300:
            print(f"      - Email sent successfully! Status Code: {response.status_code}")
        else:
            print(f"      - ❌ SendGrid API Error: Failed to send email. Status: {response.status_code}, Body: {response.body}")
    except Exception as e:
        print(f"      - ❌ An unexpected error occurred while sending email: {e}")

# --- Direct Testing Block ---
if __name__ == '__main__':
    print("--- Testing Alerting Services ---")
    test_message = "This is a test alert from the Sentinel AI system."
    test_video_path = "temp_files/test_clip.mp4"
    test_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    test_location = "Test Location, Secunderabad, India"
    send_sms_alert(test_message, test_timestamp, test_location)
    send_email_alert(test_message, test_video_path, test_timestamp, test_location)
    
    print("\n--- Test Complete ---") 