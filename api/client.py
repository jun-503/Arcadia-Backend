"""
Example client script for using the YOLOv11 Damage Detection API.
"""

import requests
import json
import sys
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000"


def check_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/api/health")
        response.raise_for_status()
        data = response.json()
        print("✅ API Health Check:")
        print(json.dumps(data, indent=2))
        return True
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Start it with: python api/main.py")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def detect_image(image_path, confidence=0.25, iou=0.45, return_image=True):
    """
    Send image to API for damage detection.
    
    Args:
        image_path: Path to image file
        confidence: Confidence threshold
        iou: IOU threshold
        return_image: Whether to save annotated image
    """
    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        return None
    
    print(f"\n📸 Processing: {image_path}")
    print("-" * 60)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            params = {
                'confidence': confidence,
                'iou': iou,
                'return_image': return_image
            }
            
            response = requests.post(
                f"{API_URL}/api/detect",
                files=files,
                params=params,
                timeout=60
            )
            response.raise_for_status()
        
        data = response.json()
        
        # Print results
        print(f"✅ Detections: {data['total_damages']} damages found")
        
        if 'statistics' in data:
            stats = data['statistics']
            print(f"\n📊 Statistics:")
            print(f"   Average Severity: {stats['average_severity']}/100")
            print(f"   Max Severity:     {stats['max_severity']}/100")
            print(f"   Min Severity:     {stats['min_severity']}/100")
            print(f"   Breakdown: LOW={stats['severity_breakdown']['LOW']}, "
                  f"MEDIUM={stats['severity_breakdown']['MEDIUM']}, "
                  f"HIGH={stats['severity_breakdown']['HIGH']}, "
                  f"CRITICAL={stats['severity_breakdown']['CRITICAL']}")
        
        if 'vehicle_assessment' in data:
            assessment = data['vehicle_assessment']
            print(f"\n🚗 Vehicle Assessment:")
            print(f"   Level: {assessment['assessment_level']}")
            print(f"   Severity: {assessment['average_severity']}/100")
        
        print(f"\n📝 Detections Details:")
        for i, det in enumerate(data['detections'], 1):
            print(f"\n   {i}. {det['class'].upper()}")
            print(f"      Confidence:  {det['confidence']:.3f}")
            print(f"      Area:        {det['area_percent']:.2f}%")
            print(f"      Severity:    {det['combined_severity']:.1f}/100 [{det['severity_level']}]")
            print(f"      Location:    {det['location_weight']:.1f}x")
        
        print("\n" + "-" * 60)
        return data
    
    except requests.exceptions.Timeout:
        print("❌ Request timeout. Image too large or API not responding.")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is it running?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
    
    return None


def batch_detect(image_dir, confidence=0.25, iou=0.45):
    """
    Process multiple images from a directory.
    
    Args:
        image_dir: Directory containing images
        confidence: Confidence threshold
        iou: IOU threshold
    """
    image_dir = Path(image_dir)
    if not image_dir.exists():
        print(f"❌ Directory not found: {image_dir}")
        return
    
    image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
    
    if not image_files:
        print(f"❌ No images found in {image_dir}")
        return
    
    print(f"\n📁 Batch Processing: {len(image_files)} images")
    print("-" * 60)
    
    try:
        files = [('files', open(f, 'rb')) for f in image_files]
        params = {
            'confidence': confidence,
            'iou': iou
        }
        
        response = requests.post(
            f"{API_URL}/api/detect/batch",
            files=files,
            params=params,
            timeout=300
        )
        response.raise_for_status()
        
        data = response.json()
        
        print(f"\n✅ Batch Complete:")
        print(f"   Total: {data['batch_size']}")
        print(f"   Successful: {data['successful']}")
        print(f"   Failed: {data['failed']}")
        
        if data['results']:
            print(f"\n📊 Results Summary:")
            for result in data['results']:
                avg_sev = result.get('average_severity', 'N/A')
                print(f"   {result['filename']}: {result['total_damages']} damages, "
                      f"avg severity={avg_sev}")
        
        if data['errors']:
            print(f"\n⚠️  Errors:")
            for error in data['errors']:
                print(f"   {error['filename']}: {error['error']}")
        
        print("\n" + "-" * 60)
        return data
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        for _, f in files:
            f.close()


def get_models():
    """List available models"""
    try:
        response = requests.get(f"{API_URL}/api/models")
        response.raise_for_status()
        data = response.json()
        
        print("\n📦 Available Models:")
        for model in data['available_models']:
            marker = "→" if model == data['current_model'] else " "
            print(f"   {marker} {model}")
        print(f"\nCurrent: {data['current_model']}")
        
        return data
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def get_config():
    """Get API configuration"""
    try:
        response = requests.get(f"{API_URL}/api/config")
        response.raise_for_status()
        data = response.json()
        
        print("\n⚙️  API Configuration:")
        print(json.dumps(data, indent=2))
        
        return data
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Main CLI"""
    if len(sys.argv) < 2:
        print("Usage: python client.py <command> [options]")
        print("\nCommands:")
        print("  health          - Check API health")
        print("  detect <image>  - Detect damage in image")
        print("  batch <dir>     - Batch process images from directory")
        print("  models          - List available models")
        print("  config          - Get API configuration")
        print("\nOptions:")
        print("  --confidence <float>  - Confidence threshold (0-1, default=0.25)")
        print("  --iou <float>         - IOU threshold (0-1, default=0.45)")
        print("\nExample:")
        print("  python client.py detect test.jpg")
        print("  python client.py detect test.jpg --confidence 0.5")
        print("  python client.py batch data/test --confidence 0.3")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "health":
        check_health()
    
    elif command == "detect" and len(sys.argv) > 2:
        image_path = sys.argv[2]
        confidence = 0.25
        iou = 0.45
        
        # Parse options
        for i, arg in enumerate(sys.argv[3:]):
            if arg == "--confidence" and i + 4 < len(sys.argv):
                confidence = float(sys.argv[i + 4])
            elif arg == "--iou" and i + 4 < len(sys.argv):
                iou = float(sys.argv[i + 4])
        
        detect_image(image_path, confidence, iou)
    
    elif command == "batch" and len(sys.argv) > 2:
        image_dir = sys.argv[2]
        confidence = 0.25
        iou = 0.45
        
        # Parse options
        for i, arg in enumerate(sys.argv[3:]):
            if arg == "--confidence" and i + 4 < len(sys.argv):
                confidence = float(sys.argv[i + 4])
            elif arg == "--iou" and i + 4 < len(sys.argv):
                iou = float(sys.argv[i + 4])
        
        batch_detect(image_dir, confidence, iou)
    
    elif command == "models":
        get_models()
    
    elif command == "config":
        get_config()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
