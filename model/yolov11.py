from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os
import json
from datetime import datetime

class YOLOv11DamageDetector:
    def __init__(self, model_name="model/weights/yolo11n.pt"):
        """
        Initialize YOLOv11 model.
        Downloads pretrained weights if not available locally.

        Args:
            model_name (str): Path to pretrained YOLOv11 weights (yolo11n.pt, best_run2.pt, etc.)
        """
        # If model_name is just a filename, check in model/weights/
        if "/" not in model_name and "\\" not in model_name:
            import os
            if os.path.exists(f"model/weights/{model_name}"):
                model_name = f"model/weights/{model_name}"
        
        self.model = YOLO(model_name)
        self.model_path = model_name

    def train(self, data_path="data/raw/data.yaml", epochs=25, batch_size=16, imgsz=416, device='mps'):
        """
        Train the YOLOv11 model.

        Args:
            data_path (str): Path to data.yaml
            epochs (int)
            batch_size (int)
            imgsz (int)
            device (int or str): GPU id or "cpu"
        """
        self.model.train(
            data=data_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            device=device,
            workers=4,
            amp=True,
            project="outputs/runs",
            name="train",
        )
    
    def finetune(self, data_path="data/raw/data.yaml", epochs=10, batch_size=16, imgsz=416, 
                 device='mps', lr0=1e-4, patience=3):
        """
        Fine-tune the YOLOv11 model with lower learning rate.
        Use this after training to improve performance on new data or additional epochs.

        Args:
            data_path (str): Path to data.yaml
            epochs (int): Number of epochs (typically 5-20 for fine-tuning)
            batch_size (int)
            imgsz (int)
            device (int or str): GPU id or "cpu"
            lr0 (float): Initial learning rate (lower for fine-tuning, default 1e-4)
            patience (int): Early stopping patience
        """
        print(f"Fine-tuning from {self.model_path} with lr0={lr0}")
        self.model.train(
            data=data_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            device=device,
            workers=4,
            amp=True,
            lr0=lr0,
            patience=patience,
            resume=False,
            project="outputs/runs",
            name="finetune",
        )

    def evaluate(self, data_path, conf=0.25, iou=0.45, max_det=1000):
        """
        Evaluate the YOLOv11 model.

        Returns:
            results dict
        """
        results = self.model.val(data=data_path, conf=conf, iou=iou, max_det=max_det)
        return results

    def predict(self, image_path, conf=0.25, iou=0.45, max_det=1000, visualize=True):
        """
        Predict damage on a single image with comprehensive severity scoring.

        Args:
            image_path (str): Path to image
            conf (float): Confidence threshold
            iou (float): IoU threshold
            max_det (int): Max detections
            visualize (bool): Overlay boxes and severity on image

        Returns:
            detections (list): Each detection with class, confidence, severity scores, and bbox
            output_image (PIL.Image): Annotated image with predictions
        """
        results = self.model.predict(
            source=image_path, conf=conf, iou=iou, max_det=max_det
        )

        # Load image
        pil_img = Image.open(image_path)
        img = np.array(pil_img)
        img_h, img_w = img.shape[:2]
        image_area = img_w * img_h

        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = r.names[cls_id]
                conf_score = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # ========== SEVERITY SCORING ==========
                
                # 1. Area-based severity (% of image)
                box_area = (x2 - x1) * (y2 - y1)
                area_percent = (box_area / image_area) * 100
                
                # Normalize area to 0-100 severity score (0-5% = low, 5-15% = medium, 15%+ = high)
                if area_percent < 1:
                    area_severity = area_percent * 10  # 0-10
                elif area_percent < 5:
                    area_severity = 10 + (area_percent - 1) * 5  # 10-30
                elif area_percent < 15:
                    area_severity = 30 + (area_percent - 5) * 7  # 30-100
                else:
                    area_severity = 100
                
                # 2. Confidence-based severity (0-100)
                # Model confidence: 0.25-1.0 → 0-100 severity
                confidence_severity = conf_score * 100
                
                # 3. Location impact (vehicle parts have different severity weights)
                # High-impact parts: windscreen, headlight, taillight, bumper (front/rear)
                # Medium: door, fender, roof, side mirror
                # Low: paint chip, paint trace
                location_weights = {
                    'windscreen': 1.5,
                    'headlight': 1.4,
                    'taillight': 1.4,
                    'bumper': 1.3,
                    'door': 1.1,
                    'fender': 1.1,
                    'roof': 1.1,
                    'mirror': 1.0,
                    'light': 1.2,
                    'paint': 0.6,
                    'dent': 1.0,
                    'scratch': 0.8,
                }
                
                # Apply location weight
                location_weight = 1.0
                for key, weight in location_weights.items():
                    if key.lower() in cls_name.lower():
                        location_weight = weight
                        break
                
                # 4. Combined severity score (weighted average)
                # Area: 50%, Confidence: 30%, Location: 20%
                combined_severity = (
                    area_severity * 0.5 +
                    confidence_severity * 0.3 +
                    (confidence_severity * location_weight) * 0.2
                )
                combined_severity = min(100, combined_severity)  # Cap at 100
                
                # 5. Severity level classification
                if combined_severity < 20:
                    severity_level = "LOW"
                    severity_color = (0, 255, 0)  # Green
                elif combined_severity < 50:
                    severity_level = "MEDIUM"
                    severity_color = (0, 255, 255)  # Yellow
                elif combined_severity < 75:
                    severity_level = "HIGH"
                    severity_color = (0, 165, 255)  # Orange
                else:
                    severity_level = "CRITICAL"
                    severity_color = (0, 0, 255)  # Red
                
                detection = {
                    "class": cls_name,
                    "confidence": round(conf_score, 3),
                    "bbox": (x1, y1, x2, y2),
                    "area_percent": round(area_percent, 2),
                    "area_severity": round(area_severity, 1),
                    "confidence_severity": round(confidence_severity, 1),
                    "location_weight": location_weight,
                    "combined_severity": round(combined_severity, 1),
                    "severity_level": severity_level,
                }
                detections.append(detection)

                if visualize:
                    # Draw bounding box with severity color
                    thickness = 3
                    cv2.rectangle(img, (x1, y1), (x2, y2), severity_color, thickness)
                    
                    # Main label with severity
                    label = f"{cls_name} | {conf_score:.2f} | {severity_level} ({combined_severity:.0f})"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.6
                    font_thickness = 2
                    
                    # Draw background for text
                    text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
                    padding = 5
                    cv2.rectangle(
                        img,
                        (x1 - padding, y1 - text_size[1] - 2 * padding),
                        (x1 + text_size[0] + padding, y1),
                        severity_color,
                        -1
                    )
                    
                    # Draw text
                    cv2.putText(
                        img,
                        label,
                        (x1, y1 - padding),
                        font,
                        font_scale,
                        (255, 255, 255),
                        font_thickness
                    )
                    
                    # Draw secondary info below
                    info_label = f"Area: {area_percent:.1f}% | Loc Weight: {location_weight:.1f}x"
                    cv2.putText(
                        img,
                        info_label,
                        (x1, y2 + 20),
                        font,
                        0.4,
                        (255, 255, 255),
                        1
                    )

        output_image = Image.fromarray(img) if visualize else None
        return detections, output_image

    def save_model(self, save_path="yolov11_trained.pt"):
        """
        Save the trained model weights.
        """
        self.model.save(save_path)


# --------------------------
# Example usage
# --------------------------

if __name__ == "__main__":
    # Initialize
    detector = YOLOv11DamageDetector(model_name="yolo11n.pt")  # pretrained nano
    print("Model initialized.")
    # Train
    detector.train(
    data_path="./data/raw/data.yaml",

    )
    print("Training completed.")

    # Evaluate
    eval_results = detector.evaluate(data_path="./data/raw/data.yaml")
    print(eval_results)

    # Predict
    detections, output_img = detector.predict("test_car.jpg", conf=0.25)
    print(detections)

    if output_img:
        output_img.save("test_car_output.jpg")
