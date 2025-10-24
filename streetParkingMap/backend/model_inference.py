"""
YOLO Model Inference Module
Handles model loading and parking status determination
"""

from ultralytics import YOLO
from typing import Dict, Optional
from PIL import Image

class ParkingDetector:
    """Wrapper for YOLO model to detect parking availability"""
    
    def __init__(self, model_path: str = 'models/weights.pt'):
        """
        Initialize the parking detector
        
        Args:
            model_path: Path to YOLO weights file
        """
        print(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)
        print("Model loaded successfully!")
        
    def run_inference(self, image: Image.Image) -> Dict:
        """
        Run YOLO inference on an image
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict with detection counts and confidences:
            {
                'parked_cars_confidence': float,
                'open_parking_confidence': float,
                'parked_cars_count': int,
                'open_parking_count': int
            }
        """
        if image is None:
            return {
                'parked_cars_confidence': 0.0,
                'open_parking_confidence': 0.0,
                'parked_cars_count': 0,
                'open_parking_count': 0
            }
        
        # Run inference with low confidence threshold
        results = self.model(image, conf=0.01, verbose=False)
        
        # Parse predictions
        parked_cars_detections = []
        open_parking_detections = []
        
        for box in results[0].boxes:
            class_name = results[0].names[int(box.cls.item())]
            confidence = box.conf.item()
            
            if class_name == "parkedCars":
                parked_cars_detections.append(confidence)
            elif class_name == "openParking":
                open_parking_detections.append(confidence)
        
        # Calculate average confidences
        avg_parked_cars = (
            sum(parked_cars_detections) / len(parked_cars_detections) 
            if parked_cars_detections else 0.0
        )
        avg_open_parking = (
            sum(open_parking_detections) / len(open_parking_detections)
            if open_parking_detections else 0.0
        )
        
        return {
            'parked_cars_confidence': avg_parked_cars,
            'open_parking_confidence': avg_open_parking,
            'parked_cars_count': len(parked_cars_detections),
            'open_parking_count': len(open_parking_detections)
        }
    
    def determine_status(self, predictions: Dict) -> str:
        """
        Determine parking status from predictions
        
        Args:
            predictions: Dict from run_inference()
            
        Returns:
            Status string: 'open_parking', 'parked_cars', 'both', or 'none'
        """
        has_parked_cars = predictions['parked_cars_confidence'] > 0
        has_open_parking = predictions['open_parking_confidence'] > 0
        
        if has_parked_cars and has_open_parking:
            return "both"
        elif has_open_parking:
            return "open_parking"
        elif has_parked_cars:
            return "parked_cars"
        else:
            return "none"

