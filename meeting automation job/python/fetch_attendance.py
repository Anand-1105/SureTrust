import mysql.connector
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# Database Configuration with your credentials
DB_CONFIG = {
    'host': '34.47.217.157', # Your Public IP Address
    'user': 'root',
    'password': 'anand', # Your specified password
    'database': 'meeting_automation'
}

# Google Admin SDK Configuration

ADMIN_USER_EMAIL = 'admin@yourworkspace-domain.com' #no email available since it is a test account
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']


def fetch_meet_attendance():
    """
    Fetches Google Meet attendance using the Admin SDK Reports API
    and inserts it into the MySQL database.
    """
    creds = None
    try:
        creds, _ = google.auth.default(scopes=SCOPES)
        delegated_creds = creds.with_subject(ADMIN_USER_EMAIL)
        
        service = build('admin', 'reports_v1', credentials=delegated_creds)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        start_time_str = start_time.isoformat() + "Z"
        
        print(f"Fetching Meet attendance logs since {start_time_str}...")

        results = service.activities().list(
            userKey='all',
            applicationName='meet',
            eventName='call_ended',
            startTime=start_time_str
        ).execute()
        
        activities = results.get('items', [])

        if not activities:
            print("No new meeting activities found.")
            return

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Successfully connected to the database.")

        for activity in activities:
            event_params = activity.get('events', [{}])[0].get('parameters', {})
            meeting_id = event_params.get('conference_id')
            participants = event_params.get('participant')

            if not meeting_id or not participants:
                continue

            print(f"Processing attendance for Meeting ID: {meeting_id}")

            for person in participants:
                email = person.get('identifier')
                duration_seconds = int(person.get('duration_seconds', 0))
                duration_minutes = round(duration_seconds / 60)

                if not email:
                    continue
                
                sql = """
                    INSERT INTO attendance (meeting_id, attendee_email, duration_minutes)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE duration_minutes = VALUES(duration_minutes);
                """
                cursor.execute(sql, (meeting_id, email, duration_minutes))

        conn.commit()
        cursor.close()
        conn.close()
        print("Finished processing and storing attendance.")

    except HttpError as error:
        print(f"An API error occurred: {error}")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        print("Error: Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
    else:
        fetch_meet_attendance()
