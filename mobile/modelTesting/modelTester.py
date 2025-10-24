import os
import cv2
import torch
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import time
import json

def get_camera_id_from_location(location: str, camera_data_path: str = '../backend/camera_id_lat_lng_wiped.json') -> str:
    """Get camera ID from location name using the camera data file"""
    try:
        with open(camera_data_path, 'r') as f:
            camera_data = json.load(f)
            if location in camera_data:
                return camera_data[location]['camera_id']
    except Exception as e:
        print(f"Error loading camera data: {e}")
    return None

class VehicleDetector:
    def __init__(self, name: str):
        self.name = name
        self.model = None
        
    def load_model(self):
        if self.name.startswith('yolo'):
            from ultralytics import YOLO
            self.model = YOLO(f"{self.name}.pt")
        elif self.name == 'fasterrcnn':
            import torchvision
            self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn_v2(
                weights="COCO_V1",
                box_score_thresh=0.5
            )
            self.model.eval()
        elif self.name == 'retinanet':
            import torchvision
            self.model = torchvision.models.detection.retinanet_resnet50_fpn_v2(
                weights="COCO_V1",
                box_score_thresh=0.5
            )
            self.model.eval()
        elif self.name == 'ssd':
            import torchvision
            self.model = torchvision.models.detection.ssdlite320_mobilenet_v3_large(
                weights="COCO_V1",
                score_thresh=0.5
            )
            self.model.eval()
            
    def detect(self, image: np.ndarray) -> Dict:
        start_time = time.time()
        
        # Track memory before processing
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            start_mem = torch.cuda.memory_allocated()
        
        if self.name.startswith('yolo'):
            results = self.model(image)
            car_detections = [box for box in results[0].boxes if box.cls.item() == 2]  # class 2 is car
            truck_detections = [box for box in results[0].boxes if box.cls.item() == 7]  # class 7 is truck
            
            car_scores = [box.conf.item() for box in car_detections]
            truck_scores = [box.conf.item() for box in truck_detections]
            
        else:
            # Convert BGR to RGB and to tensor for torch models
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_tensor = torch.from_numpy(image_rgb).permute(2, 0, 1).float() / 255.0
            image_tensor = image_tensor.unsqueeze(0)
            
            with torch.no_grad():
                predictions = self.model(image_tensor)
            
            # Get car and truck detections (COCO classes: car=3, truck=8)
            car_indices = [i for i, label in enumerate(predictions[0]['labels']) if label == 3]
            truck_indices = [i for i, label in enumerate(predictions[0]['labels']) if label == 8]
            
            car_scores = [predictions[0]['scores'][i].item() for i in car_indices]
            truck_scores = [predictions[0]['scores'][i].item() for i in truck_indices]
        
        process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Calculate memory used
        if torch.cuda.is_available():
            end_mem = torch.cuda.memory_allocated()
            memory_used = (end_mem - start_mem) / 1024**3  # Convert to GB
        else:
            memory_used = 0  # CPU mode
        
        return {
            'cars': len(car_scores),
            'trucks': len(truck_scores),
            'car_confidence': np.mean(car_scores) if car_scores else 0,
            'truck_confidence': np.mean(truck_scores) if truck_scores else 0,
            'process_time_ms': process_time,
            'memory_gb': memory_used,
            'fps': 1000 / process_time  # Convert ms to FPS
        }

class ModelTester:
    def __init__(self):
        self.test_images_dir = Path('test_images')
        self.detectors = [
            VehicleDetector('yolov8x'),
            VehicleDetector('yolov8l'),
            VehicleDetector('fasterrcnn'),
            VehicleDetector('retinanet'),
            VehicleDetector('ssd')
        ]
        
    def load_models(self):
        print("Loading models...")
        for detector in self.detectors:
            print(f"Loading {detector.name}...")
            detector.load_model()
        print("All models loaded!")
        
    def process_image(self, image_path: Path) -> Dict[str, Dict]:
        """Process a single image with all models"""
        image = cv2.imread(str(image_path))
        if image is None:
            return None
            
        results = {}
        for detector in self.detectors:
            results[detector.name] = detector.detect(image)
        return results
        
    def format_results(self, location: str, timestamp: str, results: Dict) -> str:
        """Format results for a single image"""
        # Get camera ID and generate URL
        camera_id = get_camera_id_from_location(location)
        camera_url = f'https://webcams.nyctmc.org/api/cameras/{camera_id}/image'
        
        output = [
            f"=== {location} ({timestamp}) ===",
            f"Camera URL: {camera_url}\n"
        ]
        
        # First, show vehicle counts for quick comparison
        output.append("Vehicle Counts:")
        for model_name, data in results.items():
            cars = data['cars']
            trucks = data['trucks']
            car_conf = data['car_confidence']
            truck_conf = data['truck_confidence']
            
            vehicles = []
            if cars > 0:
                vehicles.append(f"{cars} cars ({car_conf:.2f} conf)")
            if trucks > 0:
                vehicles.append(f"{trucks} trucks ({truck_conf:.2f} conf)")
                
            output.append(f"{model_name:10}: {', '.join(vehicles)}")
        
        # Then show performance metrics
        output.append("\nPerformance Metrics:")
        for model_name, data in results.items():
            output.append(f"{model_name:10}:")
            output.append(f"            Process time: {data['process_time_ms']:.0f}ms")
            output.append(f"            Memory used: {data['memory_gb']:.1f}GB")
            output.append(f"            FPS: {data['fps']:.1f}")
        
        output.append("\n" + "-" * 50 + "\n")
        return "\n".join(output)
        
    def run_evaluation(self):
        """Run evaluation on all images in test_images directory"""
        self.load_models()
        
        with open('results.txt', 'w') as f:
            f.write("MODEL EVALUATION RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            # Process all images in all batch directories
            for batch_dir in sorted(self.test_images_dir.glob("batch_*")):
                f.write(f"\nBatch: {batch_dir.name}\n")
                f.write("=" * 50 + "\n\n")
                
                for image_path in sorted(batch_dir.glob("*.jpg")):
                    # Extract location and timestamp from filename
                    parts = image_path.stem.split("_")
                    timestamp = datetime.fromtimestamp(int(parts[-1])/1000).strftime('%Y-%m-%d %H:%M:%S')
                    location = "_".join(parts[:-1])
                    
                    print(f"Processing {location}...")
                    results = self.process_image(image_path)
                    if results:
                        formatted = self.format_results(location, timestamp, results)
                        f.write(formatted)
                        print(formatted)  # Also show in console
                    else:
                        print(f"Failed to process {image_path}")

if __name__ == "__main__":
    tester = ModelTester()
    tester.run_evaluation() 