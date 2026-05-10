"""
API Usage Examples - YOLOv11 Damage Detection FastAPI

This file contains practical examples for using the API in various scenarios.
"""

# ============================================================================
# EXAMPLE 1: Python - Single Image Detection
# ============================================================================

import requests
from pathlib import Path

def detect_single_image():
    """Simple single image detection"""
    
    API_URL = "http://localhost:8000"
    
    # Open image file
    with open("test.jpg", "rb") as f:
        response = requests.post(
            f"{API_URL}/api/detect",
            files={"file": f},
            params={
                "confidence": 0.25,
                "iou": 0.45,
                "return_image": True
            }
        )
    
    # Parse response
    result = response.json()
    
    print(f"Damages detected: {result['total_damages']}")
    for damage in result['detections']:
        print(f"  - {damage['class']}: {damage['combined_severity']:.0f}/100 [{damage['severity_level']}]")
    
    if 'statistics' in result:
        print(f"Average severity: {result['statistics']['average_severity']}/100")
    
    return result


# ============================================================================
# EXAMPLE 2: Python - Batch Processing with Multiple Images
# ============================================================================

def detect_batch_images():
    """Process multiple images in one batch"""
    
    API_URL = "http://localhost:8000"
    
    # Prepare files for upload
    image_files = [
        ("files", open("image1.jpg", "rb")),
        ("files", open("image2.jpg", "rb")),
        ("files", open("image3.jpg", "rb")),
    ]
    
    try:
        response = requests.post(
            f"{API_URL}/api/detect/batch",
            files=image_files,
            params={"confidence": 0.3}
        )
        
        result = response.json()
        
        print(f"Batch Results: {result['successful']}/{result['batch_size']} successful")
        
        for res in result['results']:
            print(f"  {res['filename']}: {res['total_damages']} damages")
        
        return result
    
    finally:
        # Close all files
        for _, f in image_files:
            f.close()


# ============================================================================
# EXAMPLE 3: Python - Using Sessions for Multiple Requests
# ============================================================================

def detect_multiple_with_session():
    """Use session for multiple requests (more efficient)"""
    
    API_URL = "http://localhost:8000"
    
    with requests.Session() as session:
        images = ["car1.jpg", "car2.jpg", "car3.jpg"]
        
        results = []
        for image_path in images:
            with open(image_path, "rb") as f:
                response = session.post(
                    f"{API_URL}/api/detect",
                    files={"file": f},
                    params={"confidence": 0.25}
                )
            
            results.append(response.json())
            print(f"✅ {image_path}: {response.json()['total_damages']} damages")
        
        return results


# ============================================================================
# EXAMPLE 4: Python - Handling Errors
# ============================================================================

def detect_with_error_handling():
    """Robust error handling"""
    
    API_URL = "http://localhost:8000"
    
    try:
        # Check API is running
        health = requests.get(f"{API_URL}/api/health", timeout=5)
        if health.status_code != 200:
            print("❌ API not healthy")
            return None
        
        # Send request with timeout
        with open("test.jpg", "rb") as f:
            response = requests.post(
                f"{API_URL}/api/detect",
                files={"file": f},
                params={"confidence": 0.25},
                timeout=60
            )
        
        # Check response
        response.raise_for_status()
        
        result = response.json()
        return result
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is it running?")
    except requests.exceptions.Timeout:
        print("❌ Request timeout - image too large or API too slow")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Details: {e.response.text}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    return None


# ============================================================================
# EXAMPLE 5: Python - Custom Results Processing
# ============================================================================

def process_results_advanced():
    """Advanced result processing and filtering"""
    
    API_URL = "http://localhost:8000"
    
    with open("test.jpg", "rb") as f:
        response = requests.post(
            f"{API_URL}/api/detect",
            files={"file": f},
            params={"confidence": 0.3}
        )
    
    result = response.json()
    detections = result['detections']
    
    # Filter by severity level
    critical_damages = [d for d in detections if d['severity_level'] == 'CRITICAL']
    high_damages = [d for d in detections if d['severity_level'] == 'HIGH']
    
    print(f"Critical damages: {len(critical_damages)}")
    print(f"High damages: {len(high_damages)}")
    
    # Sort by severity
    sorted_damages = sorted(detections, key=lambda x: x['combined_severity'], reverse=True)
    
    print("\nDamages by severity:")
    for damage in sorted_damages:
        print(f"  {damage['class']:20} {damage['combined_severity']:6.1f}/100  {damage['severity_level']}")
    
    # Calculate repair cost estimate (example)
    cost_multiplier = {
        'LOW': 100,
        'MEDIUM': 500,
        'HIGH': 2000,
        'CRITICAL': 5000
    }
    
    total_cost = sum(cost_multiplier.get(d['severity_level'], 0) for d in detections)
    print(f"\nEstimated repair cost: ${total_cost}")


# ============================================================================
# EXAMPLE 6: cURL - Single Image (Bash)
# ============================================================================

# bash example:
# curl -X POST "http://localhost:8000/api/detect" \
#   -F "file=@car.jpg" \
#   -F "confidence=0.25" \
#   -F "iou=0.45" \
#   -F "return_image=true"


# ============================================================================
# EXAMPLE 7: cURL - Batch Images (Bash)
# ============================================================================

# bash example:
# curl -X POST "http://localhost:8000/api/detect/batch" \
#   -F "files=@image1.jpg" \
#   -F "files=@image2.jpg" \
#   -F "files=@image3.jpg" \
#   -F "confidence=0.3"


# ============================================================================
# EXAMPLE 8: cURL - Save Response to File (Bash)
# ============================================================================

# bash example:
# curl -X POST "http://localhost:8000/api/detect" \
#   -F "file=@car.jpg" \
#   > detection_results.json
# 
# # Pretty print JSON
# cat detection_results.json | jq .


# ============================================================================
# EXAMPLE 9: JavaScript/Node.js - Fetch API
# ============================================================================

async function detectImageJavaScript() {
    const API_URL = "http://localhost:8000";
    
    // Read file
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('confidence', 0.25);
    formData.append('iou', 0.45);
    
    try {
        // Send request
        const response = await fetch(`${API_URL}/api/detect`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        // Parse response
        const result = await response.json();
        
        console.log(`Damages found: ${result.total_damages}`);
        
        // Display results
        result.detections.forEach(damage => {
            console.log(`  ${damage.class}: ${damage.combined_severity.toFixed(0)}/100 [${damage.severity_level}]`);
        });
        
        return result;
    } catch (error) {
        console.error('Error:', error);
    }
}


// ============================================================================
// EXAMPLE 10: JavaScript - React Component
// ============================================================================

/*
import React, { useState } from 'react';

function DamageDetector() {
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const API_URL = "http://localhost:8000";
    
    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        setLoading(true);
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('confidence', 0.25);
        
        try {
            const response = await fetch(`${API_URL}/api/detect`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div>
            <input 
                type="file" 
                onChange={handleImageUpload}
                disabled={loading}
            />
            
            {loading && <p>Processing...</p>}
            
            {results && (
                <div>
                    <h2>Damages: {results.total_damages}</h2>
                    <p>Average Severity: {results.statistics.average_severity.toFixed(1)}/100</p>
                    
                    <ul>
                        {results.detections.map((det, idx) => (
                            <li key={idx}>
                                {det.class}: {det.combined_severity.toFixed(0)}/100 [{det.severity_level}]
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default DamageDetector;
*/


# ============================================================================
# EXAMPLE 11: Docker - Run API in Container
# ============================================================================

# Build image
# docker build -t yolo-damage-api:latest .

# Run container
# docker run -p 8000:8000 \
#   -v $(pwd)/model/weights:/app/model/weights:ro \
#   -v $(pwd)/data:/app/data:ro \
#   yolo-damage-api:latest

# Test from host machine
# curl -F "file=@test.jpg" http://localhost:8000/api/detect


# ============================================================================
# EXAMPLE 12: Docker Compose - Multiple Containers
# ============================================================================

# Start services
# docker-compose up -d

# View logs
# docker-compose logs -f api

# Scale API to 3 instances
# docker-compose up -d --scale api=3

# Stop services
# docker-compose down


# ============================================================================
# EXAMPLE 13: Python - Stream Images from Camera
# ============================================================================

def detect_from_camera():
    """Real-time detection from webcam (requires opencv)"""
    
    import cv2
    import requests
    from pathlib import Path
    import tempfile
    
    API_URL = "http://localhost:8000"
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process every 10th frame
        if frame_count % 10 != 0:
            continue
        
        # Save frame temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            cv2.imwrite(tmp.name, frame)
            tmp_path = tmp.name
        
        try:
            # Send to API
            with open(tmp_path, 'rb') as f:
                response = requests.post(
                    f"{API_URL}/api/detect",
                    files={"file": f},
                    params={"confidence": 0.3},
                    timeout=5
                )
            
            if response.ok:
                result = response.json()
                # Draw damages on frame
                for damage in result['detections']:
                    severity = damage['combined_severity']
                    label = f"{damage['class']}: {severity:.0f}"
                    print(f"Frame {frame_count}: {label}")
        
        except Exception as e:
            print(f"Error processing frame: {e}")
        
        finally:
            Path(tmp_path).unlink()
        
        # Display frame
        cv2.imshow('Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


# ============================================================================
# EXAMPLE 14: Integration - Save Results to Database
# ============================================================================

def save_to_database():
    """Save detection results to database (requires sqlite3)"""
    
    import sqlite3
    import requests
    from datetime import datetime
    
    API_URL = "http://localhost:8000"
    
    # Create database
    conn = sqlite3.connect('detections.db')
    c = conn.cursor()
    
    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            filename TEXT,
            class TEXT,
            severity REAL,
            confidence REAL,
            area_percent REAL
        )
    ''')
    
    # Detect damages
    with open("test.jpg", "rb") as f:
        response = requests.post(
            f"{API_URL}/api/detect",
            files={"file": f}
        )
    
    result = response.json()
    
    # Save to database
    timestamp = result['timestamp']
    filename = result['filename']
    
    for detection in result['detections']:
        c.execute('''
            INSERT INTO detections 
            (timestamp, filename, class, severity, confidence, area_percent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            filename,
            detection['class'],
            detection['combined_severity'],
            detection['confidence'],
            detection['area_percent']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Saved {len(result['detections'])} detections to database")


# ============================================================================
# EXAMPLE 15: Performance Testing - Load Test
# ============================================================================

def load_test():
    """Simple load test to measure API performance"""
    
    import requests
    import time
    from concurrent.futures import ThreadPoolExecutor
    
    API_URL = "http://localhost:8000"
    
    def send_request(image_path):
        try:
            with open(image_path, 'rb') as f:
                start = time.time()
                response = requests.post(
                    f"{API_URL}/api/detect",
                    files={"file": f},
                    timeout=30
                )
                elapsed = time.time() - start
            
            return {
                'status': 'success' if response.ok else 'error',
                'time': elapsed
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'time': None}
    
    # Send 10 concurrent requests
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(send_request, 'test.jpg')
            for _ in range(10)
        ]
        
        results = [f.result() for f in futures]
    
    # Calculate statistics
    times = [r['time'] for r in results if r['time'] is not None]
    successful = sum(1 for r in results if r['status'] == 'success')
    
    print(f"✅ Successful: {successful}/10")
    print(f"⏱️  Average time: {sum(times) / len(times):.2f}s")
    print(f"⏱️  Min time: {min(times):.2f}s")
    print(f"⏱️  Max time: {max(times):.2f}s")


# ============================================================================

if __name__ == "__main__":
    # Run examples
    print("Example 1: Single image detection")
    # detect_single_image()
    
    print("\nExample 15: Load test")
    # load_test()
