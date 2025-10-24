#!/usr/bin/env python3
"""
Setup script for Parking Spotter Traffic Data Collection System
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Initialize the SQLite database"""
    print("\n🗄️ Setting up database...")
    
    try:
        from database_setup import create_database
        db_path = create_database()
        print(f"✅ Database created at: {db_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def test_yolo_model():
    """Test if YOLOv8 model can be loaded"""
    print("\n🤖 Testing YOLOv8 model...")
    
    try:
        from ultralytics import YOLO
        model = YOLO("yolov8l.pt")  # This will download the model if needed
        print("✅ YOLOv8 model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load YOLOv8 model: {e}")
        print("The model will be downloaded automatically on first run")
        return False

def check_email_config():
    """Check if email notifications are configured"""
    print("\n📧 Checking email configuration...")
    
    try:
        from email_notifications import EMAIL_USER, EMAIL_PASSWORD
        
        if EMAIL_USER == "your_email@gmail.com" or EMAIL_PASSWORD == "your_app_password":
            print("⚠️ Email notifications not configured")
            print("To enable email alerts:")
            print("1. Edit email_notifications.py")
            print("2. Set EMAIL_USER to your Gmail address")
            print("3. Set EMAIL_PASSWORD to your Gmail App Password")
            print("4. Create App Password at: https://myaccount.google.com/apppasswords")
            return False
        else:
            print("✅ Email configuration detected")
            return True
    except Exception as e:
        print(f"❌ Error checking email config: {e}")
        return False

def create_windows_task():
    """Help create Windows Task Scheduler entry"""
    if platform.system() != "Windows":
        return
    
    print("\n⚙️ Windows Task Scheduler Setup")
    print("To run the data collection automatically:")
    print("1. Open Task Scheduler (taskschd.msc)")
    print("2. Create Basic Task")
    print("3. Name: 'Parking Spotter Data Collection'")
    print("4. Trigger: When computer starts")
    print("5. Action: Start a program")
    print(f"6. Program: {sys.executable}")
    print(f"7. Arguments: {os.path.abspath('traffic_collector.py')}")
    print(f"8. Start in: {os.path.abspath('.')}")

def main():
    """Main setup function"""
    print("🚗 Parking Spotter - Traffic Data Collection Setup")
    print("=" * 50)
    
    success_count = 0
    total_checks = 5
    
    # Check Python version
    if check_python_version():
        success_count += 1
    
    # Install dependencies
    if install_dependencies():
        success_count += 1
    
    # Setup database
    if setup_database():
        success_count += 1
    
    # Test YOLO model
    if test_yolo_model():
        success_count += 1
    
    # Check email config
    if check_email_config():
        success_count += 1
    
    # Summary
    print(f"\n📊 Setup Summary: {success_count}/{total_checks} checks passed")
    
    if success_count >= 3:
        print("✅ System is ready for data collection!")
        print(f"\nTo start collecting data:")
        print(f"cd {os.path.abspath('.')}")
        print("python traffic_collector.py")
        
        create_windows_task()
        
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
    
    print("\n🎯 Next Steps:")
    print("1. Configure email notifications (optional but recommended)")
    print("2. Run: python traffic_collector.py")
    print("3. Set up Windows Task Scheduler for auto-start (optional)")
    print("4. Monitor logs in the 'logs' folder")

if __name__ == "__main__":
    main() 