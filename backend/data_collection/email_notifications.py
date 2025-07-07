import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Email configuration
EMAIL_USER = "davidingrahamf@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "pmpj yhlh lljf rktm"  # Replace with your app password
RECIPIENT_EMAIL = "davidingrahamf@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_alert_email(subject, message, alert_type="info"):
    """Send email alert"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"[Parking Spotter] {subject}"
        
        # Email body
        body = f"""
Traffic Data Collection Alert
=============================
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Alert Type: {alert_type.upper()}

{message}

This is an automated message from your Parking Spotter traffic data collection system.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, text)
        server.quit()
        
        logging.info(f"Alert email sent successfully: {subject}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email alert: {str(e)}")
        return False

def send_failure_alert(cameras_failed, total_cameras, error_details):
    """Send alert when too many cameras fail"""
    failure_rate = (cameras_failed / total_cameras) * 100
    
    subject = f"High Failure Rate Alert - {cameras_failed}/{total_cameras} cameras failed ({failure_rate:.1f}%)"
    
    message = f"""
ALERT: High camera failure rate detected!

Failed Cameras: {cameras_failed}
Total Cameras: {total_cameras}
Failure Rate: {failure_rate:.1f}%

Error Details:
{error_details}

Please check your internet connection and system status.
The data collection script is still running and will retry failed cameras.
    """
    
    send_alert_email(subject, message, "error")

def send_startup_notification():
    """Send notification when data collection starts"""
    subject = "Data Collection Started"
    message = """
Traffic data collection has started successfully!

Collection Schedule: Every 15 minutes
Total Cameras: 216
Database: SQLite (traffic_data.db)
Email Alerts: Enabled

The system will monitor all NYC traffic cameras and collect car count data.
You will receive alerts if the failure rate exceeds 10%.
    """
    
    send_alert_email(subject, message, "info")

def send_daily_summary(cameras_processed, cameras_failed, total_batches):
    """Send daily summary email"""
    success_rate = ((cameras_processed - cameras_failed) / cameras_processed) * 100 if cameras_processed > 0 else 0
    
    subject = f"Daily Summary - {success_rate:.1f}% Success Rate"
    
    message = f"""
Daily Traffic Data Collection Summary
=====================================

Total Cameras Processed: {cameras_processed:,}
Failed Attempts: {cameras_failed:,}
Success Rate: {success_rate:.1f}%
Total Batches: {total_batches}

System Status: {"✅ HEALTHY" if success_rate > 90 else "⚠️ NEEDS ATTENTION"}

The data collection system processed {total_batches} batches today.
Data is being stored in traffic_data.db for historical analysis.
    """
    
    send_alert_email(subject, message, "summary")

def send_recovery_notification(recovery_message):
    """Send notification when system recovers from issues"""
    subject = "System Recovery - Data Collection Resumed"
    
    message = f"""
Good news! The data collection system has recovered.

Recovery Details:
{recovery_message}

The system is now operating normally and collecting traffic data.
    """
    
    send_alert_email(subject, message, "recovery")

if __name__ == "__main__":
    # Test email functionality
    print("Testing email notification system...")
    
    # Check if email credentials are set
    if EMAIL_USER == "your_email@gmail.com":
        print("⚠️ EMAIL SETUP REQUIRED!")
        print("Please edit email_notifications.py and set your email credentials:")
        print("1. EMAIL_USER = 'your_actual_email@gmail.com'")
        print("2. EMAIL_PASSWORD = 'your_app_password'")
        print("3. For Gmail, you'll need to create an App Password")
        print("   Go to: Google Account > Security > App passwords")
    else:
        # Test sending email
        if send_startup_notification():
            print("✅ Email test successful!")
        else:
            print("❌ Email test failed - check credentials and internet connection") 