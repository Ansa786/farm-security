import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Any

# Define the target classes for farm security (ensure these match your model's classes)
TARGET_CLASSES = ['human', 'elephant', 'monkey', 'cow']

class YoloDetector:
    """Handles loading the YOLOv8 model and running inference."""

    def __init__(self, model_path: str = "./models/best.pt", confidence_threshold: float = 0.5):
        """Initializes the YOLO model with your custom weights.
        
        NOTE: You must create a 'models' directory inside farm_security_backend
        and place your trained weights file ('best.pt' or similar) there.
        """
        self.model = None
        try:
            # We assume your best trained model is named 'best.pt'
            self.model = YOLO(model_path)
            print(f"YOLOv8 model loaded from {model_path}")
            self.class_names = self.model.names 
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to load YOLO model at {model_path}. Detection will be disabled. {e}")
            self.class_names = {} # Fallback
            
        self.conf_thresh = confidence_threshold

    def run_detection(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Performs object detection on a single frame."""
        if self.model is None:
            return []

        # Run inference using the loaded YOLO model
        results = self.model.predict(frame, conf=self.conf_thresh, verbose=False)
        detections = []
        
        # Process results
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = self.class_names.get(class_id, "unknown")
                
                # Check if the detected object is a target threat and meets confidence threshold
                if label in TARGET_CLASSES and float(box.conf[0]) >= self.conf_thresh:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        "label": label,
                        "confidence": float(box.conf[0]),
                        "bbox": [x1, y1, x2, y2]
                    })
        
        return detections

# Global instance for use in routes
detector = YoloDetector()