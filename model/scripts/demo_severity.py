#!/usr/bin/env python3
"""
Quick demo showing how to use severity scoring in your Python code.

Example usage of YOLOv11DamageDetector with enhanced severity metrics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from model.yolov11 import YOLOv11DamageDetector


def demo_severity_scoring():
    """
    Demo: Run inference with severity scoring and print results.
    """
    
    # Initialize detector with your trained model
    detector = YOLOv11DamageDetector(model_name="best_run2.pt")
    
    # Example image path (replace with your actual image)
    image_path = "f3.jpg"
    
    if not os.path.exists(image_path):
        print(f"ℹ️  Demo: Image not found at {image_path}")
        print("   To test, provide a real image and uncomment this code.\n")
        print("EXAMPLE OUTPUT (if image existed):\n")
        print("="*70)
        print("DETECTIONS (2 damages found):")
        print("-"*70)
        print("\n1. FRONT-BUMPER-DENT")
        print("   Confidence:           0.789 (78.9/100)")
        print("   Area:                 12.45% of image (42.3/100 severity)")
        print("   Location Weight:      1.30x")
        print("   ➜ COMBINED SEVERITY:  62.5/100 [HIGH]")
        print("   BBox:                 (37, 45) → (554, 459)\n")
        print("2. PAINT-TRACE")
        print("   Confidence:           0.654 (65.4/100)")
        print("   Area:                 2.15% of image (8.1/100 severity)")
        print("   Location Weight:      0.60x")
        print("   ➜ COMBINED SEVERITY:  34.2/100 [MEDIUM]")
        print("   BBox:                 (120, 200) → (280, 350)\n")
        print("-"*70)
        print("VEHICLE DAMAGE ASSESSMENT:")
        print("-"*70)
        print("Total damages found:     2")
        print("Average severity:        48.4/100 [MODERATE]")
        print("\nBreakdown:")
        print("  • LOW     :  0 damage(s)")
        print("  • MEDIUM  :  1 damage(s)")
        print("  • HIGH    :  1 damage(s)")
        print("  • CRITICAL:  0 damage(s)")
        print("="*70)
        return
    
    # Run inference
    detections, output_image = detector.predict(
        image_path=image_path,
        conf=0.25,
        iou=0.45,
        visualize=True
    )
    
    # Process results
    print("\n" + "="*70)
    print("SEVERITY SCORING RESULTS")
    print("="*70)
    
    for i, det in enumerate(detections, 1):
        print(f"\nDamage #{i}: {det['class'].upper()}")
        print(f"  Model Confidence:     {det['confidence']:.3f}")
        print(f"  Location:             {det['bbox']}")
        print()
        print(f"  📊 SEVERITY BREAKDOWN:")
        print(f"    • Confidence Score: {det['confidence_severity']:.1f}/100")
        print(f"    • Area Score:       {det['area_severity']:.1f}/100 ({det['area_percent']:.2f}% of image)")
        print(f"    • Location Weight:  {det['location_weight']:.2f}x")
        print()
        print(f"  ➜ COMBINED SEVERITY:  {det['combined_severity']:.1f}/100")
        print(f"     LEVEL:             {det['severity_level']}")
        print()
    
    # Summary
    print("="*70)
    avg_severity = sum(d['combined_severity'] for d in detections) / len(detections) if detections else 0
    print(f"Average Vehicle Severity: {avg_severity:.1f}/100")
    
    if avg_severity < 20:
        assessment = "MINIMAL - Nearly perfect condition"
    elif avg_severity < 50:
        assessment = "MODERATE - Minor to moderate damage"
    elif avg_severity < 75:
        assessment = "SUBSTANTIAL - Significant damage"
    else:
        assessment = "SEVERE - Extensive damage"
    
    print(f"Assessment:               {assessment}")
    print("="*70)
    
    # Save annotated image
    if output_image:
        # Convert RGBA to RGB if needed (JPEG doesn't support alpha channel)
        if output_image.mode == 'RGBA':
            output_image = output_image.convert('RGB')
        output_image.save("demo_output.jpg")
        print(f"\n✓ Annotated image saved: demo_output.jpg")


if __name__ == "__main__":
    demo_severity_scoring()
