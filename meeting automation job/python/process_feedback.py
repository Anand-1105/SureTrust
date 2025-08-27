import mysql.connector
from mysql.connector import Error

# --- CONFIGURATION ---
# Database Configuration with your credentials
DB_CONFIG = {
    'host': '34.47.217.157', # Your Public IP Address
    'user': 'root',
    'password': 'anand', # Your specified password
    'database': 'meeting_automation'
}

def log_error(cursor, feedback_id, message):
    """Logs an error message to the process_logs table."""
    try:
        # Insert a new log entry for the given feedback ID.
        sql = "INSERT INTO process_logs (feedback_id, log_message) VALUES (%s, %s)"
        cursor.execute(sql, (feedback_id, message))
        # Mark the feedback record as an error (is_processed = 2) so we don't try it again.
        update_sql = "UPDATE feedback SET is_processed = 2 WHERE id = %s"
        cursor.execute(update_sql, (feedback_id,))
    except Error as e:
        print(f"Failed to log error for feedback_id {feedback_id}: {e}")

def process_feedback():
    """
    Main function to fetch unprocessed feedback, match it with attendance,
    and update its status. This will be run by the cron job.
    """
    conn = None
    try:
        # Connect to the database
        conn = mysql.connector.connect(**DB_CONFIG)
        # Using dictionary=True makes it easier to access columns by name (e.g., feedback['id'])
        cursor = conn.cursor(dictionary=True) 
        
        print("Cron job started: Looking for unprocessed feedback...")

        # 1. Fetch all feedback records that haven't been processed yet (is_processed = 0).
        cursor.execute("SELECT * FROM feedback WHERE is_processed = 0")
        unprocessed_feedback = cursor.fetchall()

        if not unprocessed_feedback:
            print("No new feedback to process.")
            return

        print(f"Found {len(unprocessed_feedback)} unprocessed records.")

        for feedback in unprocessed_feedback:
            feedback_id = feedback['id']
            meeting_id = feedback['meeting_id']
            user_email = feedback['email']

            print(f"Processing feedback ID: {feedback_id} for meeting: {meeting_id}")

            # 2. For each feedback, check if the person who submitted it is in the attendance list for that specific meeting.
            query = "SELECT * FROM attendance WHERE meeting_id = %s AND attendee_email = %s"
            cursor.execute(query, (meeting_id, user_email))
            attendance_record = cursor.fetchone()

            # 3. Perform the matching logic.
            if attendance_record:
                # SUCCESS: A matching attendance record was found.
                print(f"  -> Match found for {user_email} in meeting {meeting_id}.")
                # Update the is_processed flag to 1 (processed successfully).
                update_query = "UPDATE feedback SET is_processed = 1 WHERE id = %s"
                cursor.execute(update_query, (feedback_id,))
            else:
                # FAILURE: No matching attendance record was found.
                print(f"  -> ERROR: No attendance record found for {user_email} in meeting {meeting_id}.")
                log_error(cursor, feedback_id, "Attendee not found in attendance log for the specified meeting ID.")
        
        # Commit all the changes (updates and error logs) made during this run.
        conn.commit()
        print("Processing complete. All changes have been committed.")

    except Error as e:
        print(f"Database error during processing: {e}")
        if conn and conn.is_connected():
            conn.rollback() # Roll back any changes if an error occurs mid-process.
    finally:
        # Ensure the database connection is always closed.
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")


if __name__ == '__main__':
    process_feedback()
