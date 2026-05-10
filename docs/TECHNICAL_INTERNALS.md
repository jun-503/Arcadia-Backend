# Technical Deep Dive: Severity Scoring Internals

## Table of Contents
1. [Overview](#overview)
2. [Detection Flow](#detection-flow)
3. [Confidence Calculation](#confidence-calculation)
4. [Area Calculation](#area-calculation)
5. [Location Weighting](#location-weighting)
6. [Severity Scoring](#severity-scoring)
7. [Severity Classification](#severity-classification)
8. [Visualization](#visualization)
9. [JSON Export](#json-export)
10. [Mathematical Formulas](#mathematical-formulas)

---

## Overview

The YOLOv11 damage detector processes images in the following pipeline:

```
Image Input
    ↓
[YOLOv11 Detection]
    ↓
Raw Detections (boxes + confidence)
    ↓
[Post-Processing Layer - Severity Scoring]
    ├─ Confidence Extraction
    ├─ Area Calculation
    ├─ Location Identification
    ├─ Severity Scoring
    └─ Classification
    ↓
Enhanced Detections (with severity metrics)
    ↓
[Visualization & Export]
    ├─ Annotated Images (color-coded)
    ├─ Console Output (formatted)
    └─ JSON Export (structured data)
```

**Key Point:** Severity scoring is entirely post-processing. The YOLOv11 model itself is unchanged and produces standard bounding boxes. All severity calculations happen after detection.

---

## Detection Flow

### Step 1: Image Input
```python
image_path = "car_damage.jpg"
pil_img = Image.open(image_path)  # PIL Image object
img = np.array(pil_img)            # Convert to numpy array
img_h, img_w = img.shape[:2]       # Get image dimensions (height, width)
image_area = img_w * img_h         # Total pixel count
```

**Example:**
- Image: 800×600 pixels
- `image_area = 800 × 600 = 480,000 pixels`

### Step 2: YOLO Inference
```python
results = self.model.predict(
    source=image_path,
    conf=0.25,      # Confidence threshold
    iou=0.45,       # Non-max suppression threshold
    max_det=1000    # Max detections per image
)
```

**What YOLO returns:**
- `results`: List of Result objects (one per image)
- `results[0].boxes`: All bounding boxes detected
- `results[0].names`: Class name mapping (0→class_name)

### Step 3: Iterate Over Detections
```python
for r in results:                    # Each image result
    for box in r.boxes:              # Each detected box
        cls_id = int(box.cls[0])     # Class ID (0-21 for 22 classes)
        cls_name = r.names[cls_id]   # Class name
        conf_score = float(box.conf[0])  # Confidence (0.0-1.0)
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bbox coordinates
```

**Example:**
```
Box 1:
  cls_id = 12
  cls_name = "front-bumper-dent"
  conf_score = 0.789
  xyxy = [37, 45, 554, 459]
```

---

## Confidence Calculation

### What is Confidence?

Confidence is the model's predicted probability that:
1. There IS an object in this bounding box (objectness)
2. The detected object matches this class (class probability)

**Formula (internal YOLO):**
```
Confidence = Objectness × Class_Probability
Range: 0.0 (no confidence) to 1.0 (100% confident)
```

### Where It Comes From

In YOLOv11, confidence is output from the detection head:
```
[x, y, w, h, objectness, class_0_prob, class_1_prob, ..., class_21_prob]
     └────────────────────┬─────────────────────────────────────────┘
                    Confidence = objectness × argmax(class_probs)
```

### Confidence Usage in Severity

Raw confidence (0.0-1.0) is converted to a severity score (0-100):

```python
confidence_severity = conf_score * 100

# Examples:
# conf_score = 0.25 → confidence_severity = 25
# conf_score = 0.50 → confidence_severity = 50
# conf_score = 0.75 → confidence_severity = 75
# conf_score = 0.99 → confidence_severity = 99
```

**Rationale:** 
- Higher confidence = model is more certain damage exists
- More certainty = higher severity weight
- Linear mapping for simplicity and interpretability

---

## Area Calculation

### Step 1: Calculate Bounding Box Area

```python
x1, y1, x2, y2 = map(int, box.xyxy[0])
box_width = x2 - x1
box_height = y2 - y1
box_area = box_width * box_height  # Area in pixels
```

**Example:**
```
Bbox: [37, 45, 554, 459]
  width = 554 - 37 = 517 pixels
  height = 459 - 45 = 414 pixels
  box_area = 517 × 414 = 214,038 pixels
```

### Step 2: Calculate Percentage of Image

```python
image_area = img_w * img_h
area_percent = (box_area / image_area) * 100

# For example:
# box_area = 214,038 pixels
# image_area = 800 × 600 = 480,000 pixels
# area_percent = (214,038 / 480,000) × 100 = 44.59%
```

### Step 3: Map Percentage to Area Severity Score

Area severity uses **tiered thresholds** because damage severity is non-linear:

```python
if area_percent < 1:
    # Very small damages (< 1%)
    # Map 0-1% → 0-10 severity
    area_severity = area_percent * 10
    # Examples:
    # 0.5% → 5 severity
    # 1.0% → 10 severity

elif area_percent < 5:
    # Small damages (1-5%)
    # Map 1-5% → 10-30 severity (steeper)
    area_severity = 10 + (area_percent - 1) * 5
    # Examples:
    # 1.0% → 10 severity
    # 3.0% → 20 severity
    # 5.0% → 30 severity

elif area_percent < 15:
    # Medium damages (5-15%)
    # Map 5-15% → 30-100 severity (steepest)
    area_severity = 30 + (area_percent - 5) * 7
    # Examples:
    # 5.0% → 30 severity
    # 10.0% → 65 severity
    # 15.0% → 100 severity

else:
    # Large damages (> 15%)
    # Cap at 100
    area_severity = 100
```

**Visualization of Thresholds:**
```
Area Severity
    ↑
100 |                    ___
    |                ___/
 75 |            ___/
    |        ___/
 50 |    ___/
    |___/
 25 |/
    |
  0 +─────────────────────────────────→ Area %
    0    1     5        15     20
    
    Slope 1: 0-1%    (10 per %)
    Slope 2: 1-5%    (5 per %)
    Slope 3: 5-15%   (7 per %)
```

**Why Tiered?**
- A 0.5% scratch is much less severe than a 1% scratch
- A 5% dent is much more severe than a 4% dent (moving toward substantial damage)
- A 20% damage is equivalently severe to 15% (both catastrophic)

---

## Location Weighting

### Step 1: Identify Damage Location

```python
cls_name = "front-bumper-dent"  # Extracted from YOLO

location_weights = {
    'windscreen': 1.5,   # Highest impact
    'headlight': 1.4,
    'taillight': 1.4,
    'bumper': 1.3,       # ← Matches "bumper"
    'door': 1.1,
    'fender': 1.1,
    'roof': 1.1,
    'mirror': 1.0,
    'light': 1.2,
    'paint': 0.6,        # Lowest impact
    'dent': 1.0,
    'scratch': 0.8,
}
```

### Step 2: Find Matching Weight

```python
location_weight = 1.0  # Default

for key, weight in location_weights.items():
    if key.lower() in cls_name.lower():
        location_weight = weight
        break
```

**Example Matching:**
```
cls_name = "front-bumper-dent"
Check: 'windscreen' in "front-bumper-dent" → False
Check: 'headlight' in "front-bumper-dent" → False
Check: 'taillight' in "front-bumper-dent" → False
Check: 'bumper' in "front-bumper-dent" → True ✓
location_weight = 1.3
```

### Step 3: Apply Weight to Severity

Location weight is applied as a **multiplier** to confidence severity:

```python
# In the combined severity formula:
confidence_severity = 78.9  # From confidence 0.789
location_weight = 1.3       # Bumper

weighted_confidence = confidence_severity * location_weight
                    = 78.9 × 1.3
                    = 102.57
                    = min(100, 102.57) = 100 (capped)
```

**Rationale:**
- **Critical parts** (windscreen): 1.5x multiplier
  - High impact on safety and cost
  - Damage here is more severe
  
- **Standard parts** (door, fender): 1.0-1.1x multiplier
  - Normal damage severity
  - Cosmetic but repairable
  
- **Cosmetic damage** (paint chip): 0.6x multiplier
  - Low repair cost
  - Minimal safety impact

---

## Severity Scoring

### The Combined Severity Formula

```python
combined_severity = (
    area_severity * 0.5 +
    confidence_severity * 0.3 +
    (confidence_severity * location_weight) * 0.2
)

# Weights: Area=50%, Confidence=30%, Location=20%
# Cap at 100: combined_severity = min(100, combined_severity)
```

### Complete Example Calculation

**Scenario:** Front bumper dent detection

**Step 1: Extract Raw Data**
```
cls_name = "front-bumper-dent"
conf_score = 0.789
bbox = [37, 45, 554, 459]
image_size = 800×600 pixels
```

**Step 2: Calculate Area Severity**
```
box_area = (554-37) × (459-45) = 517 × 414 = 214,038 pixels
image_area = 800 × 600 = 480,000 pixels
area_percent = (214,038 / 480,000) × 100 = 44.59%

Since 44.59% > 15%:
area_severity = 100
```

**Step 3: Calculate Confidence Severity**
```
confidence_severity = 0.789 × 100 = 78.9
```

**Step 4: Find Location Weight**
```
cls_name = "front-bumper-dent"
'bumper' in "front-bumper-dent" → True
location_weight = 1.3
```

**Step 5: Calculate Combined Severity**
```
combined_severity = (100 × 0.5) + (78.9 × 0.3) + (78.9 × 1.3 × 0.2)
                  = 50 + 23.67 + 20.54
                  = 94.21
                  = min(100, 94.21) = 94.21
```

**Result:**
```
{
  "class": "front-bumper-dent",
  "confidence": 0.789,
  "area_percent": 44.59,
  "area_severity": 100.0,
  "confidence_severity": 78.9,
  "location_weight": 1.3,
  "combined_severity": 94.21,
  "severity_level": "CRITICAL"  # > 75
}
```

### Mathematical Notation

$$\text{Severity} = \min\left(100, \left( A \times 0.5 \right) + \left( C \times 0.3 \right) + \left( C \times W \times 0.2 \right) \right)$$

Where:
- $A$ = Area Severity (0-100)
- $C$ = Confidence Severity (0-100)
- $W$ = Location Weight (0.6-1.5)

---

## Severity Classification

### Threshold-Based Classification

```python
if combined_severity < 20:
    severity_level = "LOW"
    severity_color = (0, 255, 0)      # BGR: Green

elif combined_severity < 50:
    severity_level = "MEDIUM"
    severity_color = (0, 255, 255)    # BGR: Yellow

elif combined_severity < 75:
    severity_level = "HIGH"
    severity_color = (0, 165, 255)    # BGR: Orange

else:  # combined_severity >= 75
    severity_level = "CRITICAL"
    severity_color = (0, 0, 255)      # BGR: Red
```

### Classification Examples

```
Score: 8.5    → Level: LOW       → Minimal damage
Score: 35.2   → Level: MEDIUM    → Moderate damage
Score: 62.7   → Level: HIGH      → Significant damage
Score: 88.1   → Level: CRITICAL  → Severe damage
```

### Vehicle-Level Assessment

After classifying all damages, calculate **average severity**:

```python
total_severity = sum(det['combined_severity'] for det in detections)
avg_severity = total_severity / len(detections) if detections else 0

# Then classify the vehicle:
if avg_severity < 20:
    vehicle_assessment = "MINIMAL"
elif avg_severity < 50:
    vehicle_assessment = "MODERATE"
elif avg_severity < 75:
    vehicle_assessment = "SUBSTANTIAL"
else:
    vehicle_assessment = "SEVERE"
```

---

## Visualization

### Image Annotation Process

```python
# 1. Create a copy of the image as numpy array
img = np.array(pil_img)

# 2. For each detection:
for det in detections:
    x1, y1, x2, y2 = det['bbox']
    cls_name = det['class']
    conf = det['confidence']
    severity_level = det['severity_level']
    combined_severity = det['combined_severity']
    
    # 3. Select color based on severity
    color = severity_color_map[severity_level]  # 🟢🟡🟠🔴
    
    # 4. Draw bounding box
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness=3)
    
    # 5. Create main label text
    label = f"{cls_name} | {conf:.2f} | {severity_level} ({combined_severity:.0f})"
    
    # 6. Draw text background
    text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    cv2.rectangle(
        img,
        (x1 - 5, y1 - text_size[1] - 10),
        (x1 + text_size[0] + 5, y1),
        color,
        -1  # Filled rectangle
    )
    
    # 7. Draw text
    cv2.putText(img, label, (x1, y1 - 5), font, font_scale, (255, 255, 255), 2)
    
    # 8. Draw secondary info
    info_label = f"Area: {det['area_percent']:.1f}% | Loc Weight: {det['location_weight']:.1f}x"
    cv2.putText(img, info_label, (x1, y2 + 20), font, 0.4, (255, 255, 255), 1)

# 9. Convert back to PIL
output_image = Image.fromarray(img)
```

### Color Scheme (BGR in OpenCV)

```python
severity_colors = {
    "LOW":      (0, 255, 0),      # 🟢 Green
    "MEDIUM":   (0, 255, 255),    # 🟡 Yellow
    "HIGH":     (0, 165, 255),    # 🟠 Orange
    "CRITICAL": (0, 0, 255),      # 🔴 Red
}
```

**Why BGR?** OpenCV uses BGR (Blue-Green-Red) instead of RGB:
- (B, G, R) = (0, 255, 0) → G=255 → Green
- (B, G, R) = (0, 255, 255) → G=255, R=255 → Yellow
- etc.

---

## JSON Export

### Data Structure

```python
json_data = {
    "timestamp": "2025-04-21T14:30:45.123456",
    "image": "car_damage.jpg",
    "model": "model/weights/best_run2.pt",
    "total_damages": 2,
    "average_severity": 48.4,
    "severity_assessment": "MODERATE",
    "detections": [
        {
            "class": "front-bumper-dent",
            "confidence": 0.789,
            "bbox": [37, 45, 554, 459],
            "area_percent": 12.45,
            "area_severity": 42.3,
            "confidence_severity": 78.9,
            "location_weight": 1.3,
            "combined_severity": 62.5,
            "severity_level": "HIGH"
        },
        # ... more detections
    ],
    "severity_breakdown": {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 1,
        "CRITICAL": 0
    }
}
```

### Serialization Process

```python
import json
from datetime import datetime

# 1. Build dictionary with all computed values
json_data = {
    "timestamp": datetime.now().isoformat(),
    "image": image_path,
    "model": weights_path,
    "total_damages": len(detections),
    "average_severity": round(avg_severity, 1),
    "severity_assessment": (
        "MINIMAL" if avg_severity < 20 else
        "MODERATE" if avg_severity < 50 else
        "SUBSTANTIAL" if avg_severity < 75 else
        "SEVERE"
    ),
    "detections": detections,  # List of detection dicts
    "severity_breakdown": severity_counts,  # Dict with counts
}

# 2. Write to JSON file
json_path = os.path.join(output_dir, f"detection_{timestamp}.json")
with open(json_path, 'w') as f:
    json.dump(json_data, f, indent=2)
```

### Parsing JSON in Backend

```python
import json

# Read JSON file
with open('detection_20250421_143045.json', 'r') as f:
    data = json.load(f)

# Access results
avg_severity = data['average_severity']  # 48.4
assessment = data['severity_assessment']  # "MODERATE"
num_damages = data['total_damages']  # 2

# Access individual detections
for det in data['detections']:
    damage_type = det['class']  # "front-bumper-dent"
    severity = det['combined_severity']  # 62.5
    level = det['severity_level']  # "HIGH"
    area = det['area_percent']  # 12.45
    
    # Use for downstream processing
    if severity > 75:
        route_to_expert()
    elif severity > 50:
        request_additional_photos()
    else:
        auto_approve()
```

---

## Mathematical Formulas

### 1. Bounding Box Area

$$\text{Box Area} = (x_2 - x_1) \times (y_2 - y_1)$$

### 2. Area as Percentage of Image

$$\text{Area \%} = \frac{\text{Box Area}}{\text{Image Area}} \times 100$$

### 3. Area Severity (Tiered)

$$A_s = \begin{cases}
\text{area\_\%} \times 10 & \text{if } \text{area\_\%} < 1\% \\
10 + (\text{area\_\%} - 1) \times 5 & \text{if } 1\% \le \text{area\_\%} < 5\% \\
30 + (\text{area\_\%} - 5) \times 7 & \text{if } 5\% \le \text{area\_\%} < 15\% \\
100 & \text{if } \text{area\_\%} \ge 15\%
\end{cases}$$

### 4. Confidence Severity

$$C_s = \text{confidence} \times 100$$

### 5. Combined Severity

$$S_{\text{combined}} = \min\left(100, (A_s \times 0.5) + (C_s \times 0.3) + (C_s \times W \times 0.2)\right)$$

### 6. Average Vehicle Severity

$$S_{\text{avg}} = \frac{\sum_{i=1}^{n} S_i}{n}$$

Where $S_i$ is the combined severity of detection $i$ and $n$ is the total number of detections.

### 7. Severity Level Classification

$$L = \begin{cases}
\text{LOW} & \text{if } S < 20 \\
\text{MEDIUM} & \text{if } 20 \le S < 50 \\
\text{HIGH} & \text{if } 50 \le S < 75 \\
\text{CRITICAL} & \text{if } S \ge 75
\end{cases}$$

---

## Weight Distribution Analysis

### Why 50-30-20?

| Component | Weight | Reasoning |
|-----------|--------|-----------|
| **Area** | 50% | Size is most indicative of damage severity. A 15% scratch is more severe than 0.5%. |
| **Confidence** | 30% | Model certainty matters, but YOLO is generally accurate. Secondary factor. |
| **Location** | 20% | Different parts have different importance. Windscreen vs paint chip. Fine-tuning factor. |

### Alternative Weight Distributions

**For insurance (cost-focused):**
```python
combined_severity = (
    area_severity * 0.6 +           # 60% - Size = Cost
    confidence_severity * 0.2 +     # 20%
    location_weight * 0.2           # 20%
)
```

**For safety (part-focused):**
```python
combined_severity = (
    area_severity * 0.3 +           # 30%
    confidence_severity * 0.3 +     # 30%
    location_weight * 0.4           # 40% - Critical parts weighted higher
)
```

**For accuracy (confidence-focused):**
```python
combined_severity = (
    area_severity * 0.3 +           # 30%
    confidence_severity * 0.5 +     # 50% - Only trust high confidence
    location_weight * 0.2           # 20%
)
```

---

## Performance Characteristics

### Time Complexity

```
Detection:      O(1) - Fixed YOLO inference time (~50-100ms)
Post-processing: O(n) - Linear in number of detections
                 ├─ For each detection:
                 │  ├─ Area calc: O(1)
                 │  ├─ Location match: O(k) where k=num_parts (~12)
                 │  ├─ Severity calc: O(1)
                 │  └─ Visualization: O(1)
                 └─ Total per detection: ~0.5-1ms

Total for 10 detections: ~50-150ms (detection) + 5-10ms (post-processing)
```

### Memory Complexity

```
Image storage:      O(h × w) - Full image in RAM
Detections:         O(n) - Linear in detections (each ~500 bytes)
Output image:       O(h × w) - Copy for annotation
Typical: 10 MB for image + 5 KB per detection
```

### Optimization Tips

```python
# ✓ Fast: Vectorized calculations
area_severity = np.clip(area_percent * 10, 0, 100)

# ✗ Slow: Loop per detection
for det in detections:
    area_percent = (box_area / image_area) * 100
    area_severity = calculate_area_severity(area_percent)
```

---

## Error Handling & Edge Cases

### Empty Detections

```python
if not detections:
    avg_severity = 0
    severity_breakdown = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    assessment = "MINIMAL"
```

### Invalid Bounding Boxes

```python
# YOLO may output invalid boxes (x1 > x2)
x1, y1, x2, y2 = box.xyxy[0]
if x1 >= x2 or y1 >= y2:
    # Skip or log warning
    continue
```

### Out-of-Bounds Boxes

```python
# Clamp to image boundaries
x1 = max(0, min(x1, img_w))
x2 = max(0, min(x2, img_w))
y1 = max(0, min(y1, img_h))
y2 = max(0, min(y2, img_h))
```

### Unknown Class Names

```python
if cls_name not in location_weights:
    location_weight = 1.0  # Default weight
```

---

## Validation & Testing

### Unit Test Example

```python
def test_area_severity():
    """Test area severity calculation"""
    assert area_severity_calc(0.5) == 5.0    # < 1%
    assert area_severity_calc(3.0) == 20.0   # 1-5%
    assert area_severity_calc(10.0) == 65.0  # 5-15%
    assert area_severity_calc(20.0) == 100.0 # >= 15%

def test_combined_severity():
    """Test combined severity formula"""
    result = combined_severity(
        area_severity=50,
        confidence_severity=80,
        location_weight=1.3
    )
    expected = (50 * 0.5) + (80 * 0.3) + (80 * 1.3 * 0.2)
    assert abs(result - expected) < 0.01

def test_severity_classification():
    """Test severity level assignment"""
    assert severity_level(10) == "LOW"
    assert severity_level(35) == "MEDIUM"
    assert severity_level(60) == "HIGH"
    assert severity_level(85) == "CRITICAL"
```

---

## Debugging Guide

### Print Intermediate Values

```python
def predict_debug(self, image_path):
    """Predict with debug output"""
    results = self.model.predict(source=image_path, conf=0.25)
    
    for r in results:
        for i, box in enumerate(r.boxes):
            print(f"\n--- Detection {i+1} ---")
            print(f"Class: {r.names[int(box.cls[0])]}")
            print(f"Raw confidence: {float(box.conf[0]):.4f}")
            print(f"Bbox: {box.xyxy[0].tolist()}")
            
            # Calculate manually
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            box_area = (x2-x1) * (y2-y1)
            area_percent = (box_area / (800*600)) * 100
            print(f"Box area: {box_area} px")
            print(f"Area %: {area_percent:.2f}%")
            
            # Continue with severity calculations...
```

### Validate Against Expected Values

```python
# If detection should be HIGH but shows MEDIUM
det = detections[0]
print(f"Combined severity: {det['combined_severity']}")  # Debug output
print(f"Expected > 50: {det['combined_severity'] > 50}")

# Check component contributions
print(f"Area contribution: {det['area_severity'] * 0.5:.1f}")
print(f"Confidence contribution: {det['confidence_severity'] * 0.3:.1f}")
print(f"Location contribution: {det['confidence_severity'] * det['location_weight'] * 0.2:.1f}")
```

---

## Summary

The severity scoring system works through:

1. **Detection**: YOLO identifies damages in images
2. **Area Analysis**: Calculates damage size as % of image with tiered weighting
3. **Confidence Extraction**: Converts model confidence (0-1) to severity (0-100)
4. **Location Weighting**: Applies multipliers based on vehicle part (0.6-1.5x)
5. **Severity Scoring**: Combines three factors with weights (50-30-20)
6. **Classification**: Groups into 4 levels (LOW/MEDIUM/HIGH/CRITICAL)
7. **Visualization**: Color-codes results and annotates images
8. **Export**: Outputs detailed JSON for downstream processing

All calculations are deterministic, transparent, and fully customizable.

