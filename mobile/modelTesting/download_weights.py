from ultralytics import YOLO
import torch
import torchvision
from pathlib import Path

def download_weights():
    # Create models directory if it doesn't exist
    models_dir = Path("modelTesting/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading YOLOv8x weights...")
    model = YOLO("yolov8x.pt")  # This will download if not already present
    
    print("Downloading YOLOv8l weights...")
    model = YOLO("yolov8l.pt")  # This will download if not already present
    
    print("Downloading FasterRCNN weights...")
    # This will download COCO weights if not present
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn_v2(weights="COCO_V1")
    
    print("Downloading RetinaNet weights...")
    model = torchvision.models.detection.retinanet_resnet50_fpn_v2(weights="COCO_V1")
    
    print("Downloading SSD MobileNetV3 weights...")
    model = torchvision.models.detection.ssdlite320_mobilenet_v3_large(weights="COCO_V1")
    
    print("All weights downloaded successfully!")

if __name__ == "__main__":
    download_weights() 