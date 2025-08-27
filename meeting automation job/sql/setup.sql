-- Create a database for the project if it doesn't exist.
CREATE DATABASE IF NOT EXISTS meeting_automation;

-- Switch to the newly created database.
USE meeting_automation;

-- Table to store feedback from Google Forms.
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_timestamp TIMESTAMP NULL,
    email VARCHAR(255) NOT NULL,
    meeting_id VARCHAR(255) NOT NULL,
    rating INT,
    comments TEXT,
    is_processed TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store meeting attendance.
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meeting_id VARCHAR(255) NOT NULL,
    attendee_email VARCHAR(255) NOT NULL,
    join_time TIMESTAMP NULL,
    leave_time TIMESTAMP NULL,
    duration_minutes INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_attendee_per_meeting (meeting_id, attendee_email)
);

-- Table to log any processing errors.
CREATE TABLE IF NOT EXISTS process_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_id INT,
    log_message VARCHAR(255),
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedback(id)
);
