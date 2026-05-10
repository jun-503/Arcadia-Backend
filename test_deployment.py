#!/usr/bin/env python3

"""
API Deployment Test Script
Verifies that the deployed API is working correctly
"""

import requests
import json
import sys
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this for remote deployment
TIMEOUT = 10

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_connection():
    """Test if API is reachable"""
    print_header("Testing API Connection")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success(f"API is reachable at {API_BASE_URL}")
            return True
        else:
            print_error(f"API returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {API_BASE_URL}")
        print_info("Make sure the API is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False

def test_health():
    """Test health check endpoint"""
    print_header("Testing Health Check Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_models():
    """Test models endpoint"""
    print_header("Testing Models Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/api/models", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            models = data.get('available_models', [])
            current = data.get('current_model')
            
            print_success("Models endpoint working")
            print(f"  Current Model: {current}")
            print(f"  Available Models: {len(models)}")
            for model in models:
                print(f"    - {model}")
            return True
        else:
            print_error(f"Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Models error: {str(e)}")
        return False

def test_config():
    """Test configuration endpoint"""
    print_header("Testing Configuration Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/api/config", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success("Configuration endpoint working")
            
            print(f"  Device: {data.get('device')}")
            print(f"  Confidence Threshold: {data.get('confidence_threshold')}")
            print(f"  IOU Threshold: {data.get('iou_threshold')}")
            print(f"  Max File Size: {data.get('max_file_size_mb')} MB")
            print(f"  Max Batch Size: {data.get('max_batch_size')}")
            return True
        else:
            print_error(f"Config endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Config error: {str(e)}")
        return False

def test_detection():
    """Test detection endpoint with sample image"""
    print_header("Testing Detection Endpoint")
    
    # Create a simple test image (small red square)
    try:
        from PIL import Image
        import io
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        
        print_info("Sending test image for detection...")
        response = requests.post(
            f"{API_BASE_URL}/api/detect",
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Detection endpoint working")
            print(f"  Total Damages Detected: {data.get('total_damages')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            
            stats = data.get('statistics', {})
            print(f"  Average Severity: {stats.get('average_severity', 0):.2f}")
            
            assessment = data.get('vehicle_assessment', {})
            print(f"  Assessment: {assessment.get('assessment_level')}")
            
            return True
        else:
            print_error(f"Detection failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except ImportError:
        print_info("PIL not available, skipping image generation test")
        return True
    except Exception as e:
        print_error(f"Detection error: {str(e)}")
        return False

def test_batch():
    """Test batch detection endpoint"""
    print_header("Testing Batch Detection Endpoint")
    
    try:
        from PIL import Image
        import io
        
        # Create multiple test images
        files = []
        for i in range(2):
            img = Image.new('RGB', (100, 100), color=(i*50, i*50, i*50))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            files.append(('files', ('test_{}.jpg'.format(i), img_bytes, 'image/jpeg')))
        
        print_info("Sending 2 test images for batch detection...")
        response = requests.post(
            f"{API_BASE_URL}/api/detect/batch",
            files=files,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Batch detection endpoint working")
            print(f"  Batch Size: {data.get('batch_size')}")
            print(f"  Successful: {data.get('successful')}")
            print(f"  Failed: {data.get('failed')}")
            return True
        else:
            print_error(f"Batch detection failed: {response.status_code}")
            return False
            
    except ImportError:
        print_info("PIL not available, skipping batch test")
        return True
    except Exception as e:
        print_error(f"Batch error: {str(e)}")
        return False

def run_all_tests():
    """Run all deployment tests"""
    print(f"{BLUE}")
    print("╔════════════════════════════════════════════╗")
    print("║  YOLOv11 Damage Detection API Test Suite   ║")
    print("╚════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"\nTesting API at: {API_BASE_URL}")
    print(f"Timeout: {TIMEOUT}s\n")
    
    tests = [
        ("Connection Test", test_connection),
        ("Health Check", test_health),
        ("Models Endpoint", test_models),
        ("Configuration", test_config),
        ("Detection", test_detection),
        ("Batch Detection", test_batch),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False))
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {name}")
    
    print(f"\n{BLUE}{'='*50}{RESET}")
    if passed == total:
        print(f"{GREEN}✓ All tests passed ({passed}/{total}){RESET}")
        print(f"{BLUE}{'='*50}{RESET}\n")
        return True
    else:
        print(f"{RED}✗ Some tests failed ({passed}/{total}){RESET}")
        print(f"{BLUE}{'='*50}{RESET}\n")
        return False

if __name__ == "__main__":
    # Allow custom API URL
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1]
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
