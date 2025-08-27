# Automated Google Meet Feedback and Attendance Processor

This project automates the process of collecting feedback and attendance from Google Meet sessions, processing the data, and storing it in a MySQL database.

## Workflow Overview

1.  **Data Ingestion**: A Google Form is used to collect meeting feedback from users.
2.  **Staging**: An attached Google Sheet receives the form responses.
3.  **Automation**: A Google Apps Script triggers on every form submission, sending the data directly to a Google Cloud SQL database.
4.  **Attendance Collection**: A separate Python script, using the Google Workspace Admin SDK, runs periodically to fetch attendance logs for recent meetings and stores them in the database.
5.  **Data Processing**: A final Python script runs as a cron job to match feedback submissions with attendance records, flagging each record as processed or marking it with an error.

## Project Setup

### Step 1: Google Form & Sheet
1.  Create a Google Form with the following fields:
    * Enable the setting to automatically collect the respondent's **email address** (set to "Verified").
    * A **required** short answer question titled "Meeting ID".
    * A linear scale question titled "Rating" from 1 to 5.
    * A paragraph question titled "Comments".
2.  Link the form to a new Google Sheet to collect responses.

### Step 2: Google Cloud SQL Database
1.  Create a new Google Cloud Project.
2.  Create a Google Cloud SQL for MySQL instance.
3.  Configure the instance to have a **Public IP** and add the Google Apps Script IP ranges to the **Authorized Networks** to allow connections.
4.  Connect to the instance using a MySQL client (like MySQL Workbench) and run the `sql/setup.sql` script to create the necessary database and tables.

### Step 3: Google Apps Script
1.  From the linked Google Sheet, open the Apps Script editor (`Extensions > Apps Script`).
2.  Paste the code from `google_apps_script/form_to_mysql.js` into the editor.
3.  Update the `dbConfig` variable with your Cloud SQL instance's credentials.
4.  Link the script to your Google Cloud Project in the script's Project Settings.
5.  Run the `createSubmitTrigger` function once to activate the automation.

### Step 4: Python Scripts Setup
1.  Set up a server or virtual machine where you can run Python scripts and cron jobs.
2.  Install the required Python libraries:
    ```bash
    pip install mysql-connector-python google-auth google-api-python-client
    ```
3.  **For `fetch_attendance.py`**:
    * Enable the **Admin SDK API** in your Google Cloud Project.
    * Create a **Service Account**, generate a JSON key, and download it.
    * In your Google Workspace Admin Console, delegate domain-wide authority to the service account.
    * Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable on your server to the path of the downloaded JSON key file.
4.  Update the `DB_CONFIG` variables in both `fetch_attendance.py` and `process_feedback.py` with your database credentials.

### Step 5: Schedule Cron Jobs
1.  Open your server's crontab (`crontab -e`).
2.  Schedule both Python scripts to run periodically. It's recommended to run the attendance script slightly before the processing script.
    ```bash
    # Example: Run attendance script at 5 past the hour, and processing at 10 past the hour
    5 * * * * /usr/bin/python3 /path/to/scripts/fetch_attendance.py >> /path/to/logs/cron.log 2>&1
    10 * * * * /usr/bin/python3 /path/to/scripts/process_feedback.py >> /path/to/logs/cron.log 2>&1
    ```
