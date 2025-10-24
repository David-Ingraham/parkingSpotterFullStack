@echo off
cd /d "C:\parkingSpotter\backend\data_collection"
call "traffic_env\Scripts\activate.bat"
python traffic_collector.py
pause 