# 🚗 Parking Spotter - Traffic Data Collection System

This system automatically collects traffic data from 216 NYC traffic cameras every 15 minutes using YOLOv8 computer vision to count vehicles. The data is stored in a local SQLite database for historical analysis.

## 📋 **System Overview**

- **216 cameras** processed every 15 minutes
- **YOLOv8 Large model** for high-accuracy car counting
- **SQLite database** for persistent data storage
- **Email alerts** for failure notifications
- **Parallel processing** (8 cameras simultaneously)
- **Recovery system** for power/network outages
- **Detailed logging** for monitoring

## 🏗️ **Quick Setup**

### 1. **Run Setup Script**
```bash
cd backend/data_collection
python setup.py
```

This will:
- ✅ Check Python version (3.8+ required)
- 📦 Install all dependencies
- 🗄️ Create SQLite database
- 🤖 Download YOLOv8 model
- 📧 Check email configuration

### 2. **Configure Email Notifications (Optional)**
Edit `email_notifications.py`:
```python
EMAIL_USER = "your_email@gmail.com"          # Your Gmail address
EMAIL_PASSWORD = "your_app_password"         # Gmail App Password
```

**To create Gmail App Password:**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication
3. Go to "App passwords"
4. Generate password for "Mail"
5. Use this password in the script

### 3. **Start Data Collection**
```bash
python traffic_collector.py
```

## 🔧 **Manual Setup (If Needed)**

### **Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Initialize Database**
```bash
python database_setup.py
```

### **Test Email System**
```bash
python email_notifications.py
```

## 📊 **Database Schema**

### **car_count_history** (Main Data Table)
```sql
id                INTEGER PRIMARY KEY
camera_address    TEXT                 -- Camera location (e.g., "10_Ave_42_St")
timestamp         TEXT                 -- When count was taken
car_count         INTEGER              -- Number of cars detected
confidence_score  REAL                 -- YOLOv8 confidence (0-1)
processing_time   REAL                 -- Time to process image (seconds)
created_at        TEXT                 -- Record creation time
```

### **processing_status** (Batch Tracking)
```sql
id                INTEGER PRIMARY KEY
batch_timestamp   TEXT                 -- When batch started
cameras_processed INTEGER              -- Successfully processed cameras
cameras_failed    INTEGER              -- Failed cameras
total_cameras     INTEGER              -- Total cameras in batch
processing_time   REAL                 -- Total batch processing time
status            TEXT                 -- "completed" or "partial"
```

## 📈 **Data Collection Details**

### **Schedule**
- **Every 15 minutes**: Full camera batch processing
- **~1,400 images/day**: 216 cameras × 96 intervals
- **~42,000 images/month**: Comprehensive historical data

### **Processing Pipeline**
1. **Fetch images** from NYC traffic camera API
2. **YOLOv8 analysis** to count vehicles (cars, trucks, buses, motorcycles)
3. **Database storage** with timestamps and metadata
4. **Error handling** for failed cameras
5. **Email alerts** if >10% cameras fail

### **Performance**
- **8 parallel threads** for concurrent processing
- **~13-15 minutes** to process all 216 cameras
- **High accuracy** using YOLOv8 Large model
- **Robust error handling** with automatic retries

## 📧 **Email Notifications**

### **Alert Types**
- **Startup notification**: System started successfully
- **High failure rate**: >10% cameras failed in a batch
- **Recovery notification**: System recovered from issues

### **Example Alert**
```
Subject: [Parking Spotter] High Failure Rate Alert - 25/216 cameras failed (11.6%)

ALERT: High camera failure rate detected!

Failed Cameras: 25
Total Cameras: 216
Failure Rate: 11.6%

Please check your internet connection and system status.
```

## 🔄 **Persistence & Recovery**

### **Power Outage Recovery**
- SQLite database survives reboots
- Processing resumes automatically
- No data loss from interrupted batches

### **Network Interruption Handling**
- Failed cameras are retried in next batch
- System continues processing working cameras
- Detailed error logging for troubleshooting

### **Auto-Restart Setup**
Create Windows Task Scheduler entry:
1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task: "Parking Spotter Data Collection"
3. Trigger: "When computer starts"
4. Program: `python.exe`
5. Arguments: `path\to\traffic_collector.py`
6. Start in: `path\to\data_collection\`

## 📁 **File Structure**
```
backend/data_collection/
├── traffic_collector.py       # Main data collection script
├── database_setup.py          # Database initialization
├── email_notifications.py     # Email alert system
├── setup.py                   # Automated setup script
├── requirements.txt           # Python dependencies
├── traffic_data.db            # SQLite database (created automatically)
├── logs/                      # Daily log files
│   ├── 2024-07-15.log
│   └── 2024-07-16.log
└── README.md                  # This file
```

## 📊 **Storage Requirements**

- **~42 MB/month** for raw data
- **~100-200 MB/month** with SQLite overhead
- **~2.4 GB/year** total storage needed
- Your system has **79.8 GB free** - more than sufficient!

## 🔍 **Monitoring & Logs**

### **Daily Log Files**
Located in `logs/YYYY-MM-DD.log`:
```
2024-07-15 14:25:03 - INFO - Starting batch processing at 2024-07-15 14:25:03
2024-07-15 14:26:47 - INFO - Batch complete: 210/216 cameras processed (2.8% failure rate) in 104.2s
```

### **Progress Monitoring**
Real-time progress bar shows:
```
Processing cameras: 78%|████████▌  | 168/216 [02:14<00:38, 1.24it/s]
```

### **Database Queries**
Check data collection progress:
```sql
-- Total records collected
SELECT COUNT(*) FROM car_count_history;

-- Average cars per camera today
SELECT camera_address, AVG(car_count) as avg_cars 
FROM car_count_history 
WHERE DATE(timestamp) = DATE('now')
GROUP BY camera_address;

-- Batch success rate
SELECT status, COUNT(*) 
FROM processing_status 
GROUP BY status;
```

## 🚨 **Troubleshooting**

### **Common Issues**

**Model Download Fails**
```bash
# Manually download YOLOv8 model
python -c "from ultralytics import YOLO; YOLO('yolov8l.pt')"
```

**Email Alerts Not Working**
- Check Gmail App Password is correct
- Verify 2FA is enabled on Gmail account
- Test with: `python email_notifications.py`

**High Failure Rate**
- Check internet connection stability
- Verify camera API is accessible
- Review logs for specific error patterns

**Database Errors**
- Ensure SQLite is installed
- Check disk space availability
- Verify write permissions

### **Performance Optimization**

**Slow Processing**
- Reduce `MAX_CONCURRENT_CAMERAS` from 8 to 4
- Switch to YOLOv8 Nano model for speed: `MODEL_PATH = "yolov8n.pt"`
- Increase processing interval to 20 minutes

**Memory Issues**
- Close other applications during processing
- Monitor RAM usage with Task Manager
- Consider smaller YOLO model

## 📈 **Data Analysis Examples**

After one month of collection, you can query:

```sql
-- Sunday noon traffic patterns
SELECT camera_address, AVG(car_count) as avg_sunday_noon
FROM car_count_history 
WHERE strftime('%w', timestamp) = '0'  -- Sunday
AND strftime('%H', timestamp) = '12'   -- Noon hour
GROUP BY camera_address
ORDER BY avg_sunday_noon DESC;

-- Busiest cameras overall
SELECT camera_address, AVG(car_count) as avg_cars, COUNT(*) as samples
FROM car_count_history 
GROUP BY camera_address
ORDER BY avg_cars DESC
LIMIT 10;

-- Traffic trends by hour of day
SELECT strftime('%H', timestamp) as hour, AVG(car_count) as avg_cars
FROM car_count_history 
GROUP BY hour
ORDER BY hour;
```

## 🎯 **Next Steps After Data Collection**

Once you have a month of historical data:

1. **Calculate baselines** for each camera by hour/day
2. **Implement real-time traffic classification** (light/moderate/heavy)
3. **Build frontend heat map** showing current traffic levels
4. **Add API endpoints** for traffic data access
5. **Create push notifications** for traffic changes

---

## 📞 **Support**

- **Logs**: Check `logs/` folder for detailed error information
- **Database**: Use any SQLite browser to inspect data
- **Email**: Monitor `davidingrahamf@gmail.com` for system alerts

**System Requirements:**
- Python 3.8+
- 4GB+ RAM
- 10GB+ free disk space
- Stable internet connection
- Windows 10+ (for Task Scheduler) 