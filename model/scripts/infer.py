#!/usr/bin/env python3
"""
Run inference on images using the fine-tuned YOLOv11 damage detector with severity scoring.

Usage:
    python model/scripts/infer.py --image path/to/image.jpg --weights model/weights/best_run2.pt
    python model/scripts/infer.py --image path/to/image.jpg --conf 0.5 --output outputs/predictions/
    python model/scripts/infer.py --image path/to/image.jpg --json  # Save results as JSON
"""

import argparse
import os,sys
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from model.yolov11 import YOLOv11DamageDetector


def infer_with_severity(
    image_path,
    weights="model/weights/best_run2.pt",
    conf=0.25,
    iou=0.45,
    device="mps",
    output_dir="outputs/predictions",
    save_json=False,
):
    """
    Run inference on an image with comprehensive severity scoring.

    Args:
        image_path: Path to input image
        weights: Path to model weights
        conf: Confidence threshold
        iou: IoU threshold
        device: Device ('mps', 0 for GPU, 'cpu')
        output_dir: Output directory for results
        save_json: Save results as JSON
    """
    print(f"\n{'='*70}")
    print(f"  YOLOv11 Damage Detection with Severity Scoring")
    print(f"{'='*70}")
    print(f"  Image:       {image_path}")
    print(f"  Weights:     {weights}")
    print(f"  Conf:        {conf}")
    print(f"  Device:      {device}")
    print(f"{'='*70}\n")

    # Check image exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load model and run inference
    detector = YOLOv11DamageDetector(model_name=weights)
    detections, output_image = detector.predict(
        image_path=image_path,
        conf=conf,
        iou=iou,
        visualize=True
    )

    # Print detailed results
    print(f"\n{'─'*70}")
    print(f"DETECTIONS ({len(detections)} damages found):")
    print(f"{'─'*70}\n")

    total_severity = 0
    for i, det in enumerate(detections, 1):
        print(f"{i}. {det['class'].upper()}")
        print(f"   Confidence:           {det['confidence']:.3f} ({det['confidence_severity']:.1f}/100)")
        print(f"   Area:                 {det['area_percent']:.2f}% of image ({det['area_severity']:.1f}/100 severity)")
        print(f"   Location Weight:      {det['location_weight']:.2f}x")
        print(f"   ➜ COMBINED SEVERITY:  {det['combined_severity']:.1f}/100 [{det['severity_level']}]")
        print(f"   BBox:                 ({det['bbox'][0]}, {det['bbox'][1]}) → ({det['bbox'][2]}, {det['bbox'][3]})")
        print()
        total_severity += det['combined_severity']

    avg_severity = total_severity / len(detections) if detections else 0
    
    # Overall vehicle damage assessment
    print(f"{'─'*70}")
    print(f"VEHICLE DAMAGE ASSESSMENT:")
    print(f"{'─'*70}")
    print(f"Total damages found:     {len(detections)}")
    print(f"Average severity:        {avg_severity:.1f}/100", end="")
    if avg_severity < 20:
        print(" [MINIMAL]")
    elif avg_severity < 50:
        print(" [MODERATE]")
    elif avg_severity < 75:
        print(" [SUBSTANTIAL]")
    else:
        print(" [SEVERE]")
    
    # Breakdown by severity level
    severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for det in detections:
        severity_counts[det['severity_level']] += 1
    
    print(f"\nBreakdown:")
    for level, count in severity_counts.items():
        if count > 0:
            print(f"  • {level:8s}: {count:2d} damage(s)")
    print()

    # Save annotated image
    if output_image:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_filename = f"detection_{timestamp}.jpg"
        img_path = os.path.join(output_dir, img_filename)
        output_image.save(img_path)
        print(f"✓ Annotated image saved: {img_path}")

    # Save results as JSON
    if save_json:
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "image": image_path,
            "model": weights,
            "total_damages": len(detections),
            "average_severity": round(avg_severity, 1),
            "detections": detections,
            "severity_breakdown": severity_counts,
        }
        json_filename = f"detection_{timestamp}.json"
        json_path = os.path.join(output_dir, json_filename)
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"✓ Results saved:         {json_path}")

    print(f"\n{'='*70}\n")

    return detections, output_image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="YOLOv11 Damage Detection with Severity Scoring"
    )
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument(
        "--weights",
        type=str,
        default="model/weights/best_run2.pt",
        help="Path to model weights",
    )
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold")
    parser.add_argument(
        "--device", type=str, default="mps", help="Device (mps, 0 for GPU, cpu)"
    )
    parser.add_argument(
        "--output", type=str, default="outputs/predictions", help="Output directory"
    )
    parser.add_argument(
        "--json", action="store_true", help="Save results as JSON"
    )

    args = parser.parse_args()

    infer_with_severity(
        image_path=args.image,
        weights=args.weights,
        conf=args.conf,
        iou=args.iou,
        device=args.device,
        output_dir=args.output,
        save_json=args.json,
    )
