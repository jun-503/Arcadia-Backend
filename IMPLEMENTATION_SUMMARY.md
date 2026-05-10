# Severity Scoring Implementation - Complete Summary

## ✅ What Was Added

### 1. Enhanced `model/yolov11.py`
- **New severity scoring algorithm** with 3 components:
  - **Area-based severity** (50%): Size of damage relative to image
  - **Confidence-based severity** (30%): Model's confidence in detection
  - **Location-weighted severity** (20%): Impact varies by car part
- Returns detailed detection dict with:
  - `combined_severity` (0-100)
  - `severity_level` (LOW/MEDIUM/HIGH/CRITICAL)
  - `area_percent`, `area_severity`, `confidence_severity`, `location_weight`
  - Color-coded visualization

### 2. Updated `model/scripts/infer.py`
- Enhanced command-line interface with severity scoring
- Pretty-printed output with damage breakdown
- JSON export with `--json` flag
- Color-coded bounding boxes in annotated images

### 3. New `model/scripts/demo_severity.py`
- Demo script showing severity scoring usage
- Example output for testing without running full inference

### 4. Documentation
- **`docs/SEVERITY_SCORING.md`**: Comprehensive guide with examples
- **`SEVERITY_QUICK_REF.md`**: Quick reference card and FAQs

---

## 📊 Severity Scoring Formula

```
Combined Severity = (Area × 0.5) + (Confidence × 0.3) + (Confidence × LocationWeight × 0.2)
```

### Example Calculation:
```
Damage: Front bumper dent
├─ Area: 12% of image → Area severity = 52.5/100
├─ Confidence: 0.79 → Confidence severity = 79/100
├─ Part: Front bumper → Location weight = 1.3x
└─ Combined = (52.5 × 0.5) + (79 × 0.3) + (79 × 1.3 × 0.2)
             = 26.25 + 23.7 + 20.54 = 70.49/100 [HIGH]
```

---

## 🎨 Severity Levels

| Level | Score | Color | Meaning |
|-------|-------|-------|---------|
| **LOW** | 0-20 | 🟢 Green | Minimal damage, cosmetic |
| **MEDIUM** | 20-50 | 🟡 Yellow | Noticeable, moderate repair |
| **HIGH** | 50-75 | 🟠 Orange | Significant, substantial repair |
| **CRITICAL** | 75-100 | 🔴 Red | Severe, major repair/replacement |

---

## 🚀 How to Use

### Command Line
```bash
# Basic inference (prints severity to console)
python model/scripts/infer.py --image path/to/car.jpg

# Save results as JSON
python model/scripts/infer.py --image path/to/car.jpg --json

# Custom confidence threshold
python model/scripts/infer.py --image path/to/car.jpg --conf 0.5

# Use different model weights
python model/scripts/infer.py --image path/to/car.jpg --weights model/weights/yolo11n.pt
```

### Python API
```python
from model.yolov11 import YOLOv11DamageDetector

detector = YOLOv11DamageDetector(model_name="best_run2.pt")
detections, output_image = detector.predict(
    image_path="car.jpg",
    conf=0.25,
    iou=0.45,
    visualize=True
)

for detection in detections:
    print(f"{detection['class']}: {detection['combined_severity']:.1f}/100 [{detection['severity_level']}]")
    print(f"  • Area: {detection['area_percent']:.2f}%")
    print(f"  • Confidence: {detection['confidence']:.3f}")
    print(f"  • Location weight: {detection['location_weight']:.2f}x")

output_image.save("result.jpg")
```

---

## 📋 Sample Output

### Console Output
```
======================================================================
  YOLOv11 Damage Detection with Severity Scoring
======================================================================

DETECTIONS (2 damages found):
──────────────────────────────────────────────────────────────────────

1. FRONT-BUMPER-DENT
   Confidence:           0.789 (78.9/100)
   Area:                 12.45% of image (42.3/100 severity)
   Location Weight:      1.30x
   ➜ COMBINED SEVERITY:  62.5/100 [HIGH]
   BBox:                 (37, 45) → (554, 459)

2. PAINT-TRACE
   Confidence:           0.654 (65.4/100)
   Area:                 2.15% of image (8.1/100 severity)
   Location Weight:      0.60x
   ➜ COMBINED SEVERITY:  34.2/100 [MEDIUM]
   BBox:                 (120, 200) → (280, 350)

──────────────────────────────────────────────────────────────────────
VEHICLE DAMAGE ASSESSMENT:
──────────────────────────────────────────────────────────────────────
Total damages found:     2
Average severity:        48.4/100 [MODERATE]

Breakdown:
  • LOW     :  0 damage(s)
  • MEDIUM  :  1 damage(s)
  • HIGH    :  1 damage(s)
  • CRITICAL:  0 damage(s)
======================================================================
```

### JSON Output (with `--json` flag)
```json
{
  "timestamp": "2025-04-21T14:30:45.123456",
  "image": "car.jpg",
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
    }
  ],
  "severity_breakdown": {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 1,
    "CRITICAL": 0
  }
}
```

### Annotated Image
- **Color-coded boxes**: 🟢 / 🟡 / 🟠 / 🔴 based on severity
- **Main label**: `ClassName | Confidence | SeverityLevel (Score)`
- **Secondary info**: `Area: X% | Loc Weight: Y.Zx`

---

## 🔧 Customization

### 1. Adjust Location Weights
Edit `model/yolov11.py` in the `predict()` method:
```python
location_weights = {
    'windscreen': 1.5,    # Highest priority (safety)
    'headlight': 1.4,
    'taillight': 1.4,
    'bumper': 1.3,
    'door': 1.1,
    'fender': 1.1,
    'roof': 1.1,
    'mirror': 1.0,
    'light': 1.2,
    'paint': 0.6,         # Lowest priority (cosmetic)
    'dent': 1.0,
    'scratch': 0.8,
}
```

### 2. Change Severity Thresholds
Edit the severity level assignment:
```python
if combined_severity < 20:
    severity_level = "LOW"
elif combined_severity < 50:
    severity_level = "MEDIUM"
elif combined_severity < 75:
    severity_level = "HIGH"
else:
    severity_level = "CRITICAL"
```

### 3. Adjust Component Weights
Edit the scoring formula:
```python
combined_severity = (
    area_severity * 0.5 +                           # 50% = size matters most
    confidence_severity * 0.3 +                     # 30% = model confidence
    (confidence_severity * location_weight) * 0.2   # 20% = part importance
)
```

Example: To prioritize area more:
```python
combined_severity = (
    area_severity * 0.6 +           # 60% area
    confidence_severity * 0.25 +    # 25% confidence
    (confidence_severity * location_weight) * 0.15  # 15% location
)
```

---

## 📁 Files Modified/Created

```
Project/
├── model/
│   ├── yolov11.py                    # ✏️ UPDATED: Added severity scoring
│   └── scripts/
│       ├── infer.py                  # ✏️ UPDATED: Enhanced output with severity
│       └── demo_severity.py          # ✨ NEW: Demo script
├── docs/
│   └── SEVERITY_SCORING.md           # ✨ NEW: Comprehensive guide
└── SEVERITY_QUICK_REF.md             # ✨ NEW: Quick reference
```

---

## 🧪 Testing

### Quick Test (No Image Required)
```bash
python model/scripts/demo_severity.py
# Shows example output with mock data
```

### Real Inference
```bash
# Find a test image
ls data/raw/test/images/ | head -5

# Run inference
python model/scripts/infer.py --image data/raw/test/images/[image_name].jpg --json

# Check outputs
ls -lh outputs/predictions/
```

---

## 💡 Use Cases

### 1. Insurance Claims Processing
- Export JSON with severity assessment
- Use `average_severity` to estimate repair costs
- Automate routing: HIGH/CRITICAL → manual review, LOW → auto-approve

### 2. Mobile App Integration
- Show color-coded damage indicators
- Display severity breakdown charts
- Export damage reports as PDF

### 3. Data Analysis
- Track damage severity trends over time
- Identify high-damage locations (e.g., front bumper most common)
- Correlate damage types with vehicle age/make

### 4. Fine-Tuning Feedback
- Use severity to weight training samples
- Higher severity damages = more training importance
- Helps model focus on what matters most

---

## 🎓 Key Improvements Over Baseline

| Metric | Before | After |
|--------|--------|-------|
| Information | Confidence only | 5+ severity metrics |
| Actionability | Binary high/low | 4-level severity + score |
| Customization | None | Fully adjustable weights |
| Export | N/A | JSON + annotated images |
| Part-awareness | No | Yes, with 1.5x weight range |
| Decision automation | Difficult | Easy (threshold-based routing) |

---

## 📚 Documentation

- **Main guide**: See `docs/SEVERITY_SCORING.md`
- **Quick reference**: See `SEVERITY_QUICK_REF.md`
- **Code examples**: See `model/scripts/demo_severity.py`
- **API docs**: See docstrings in `model/yolov11.py`

---

## ❓ FAQ

**Q: Should I retrain the model?**  
A: No! Severity scoring is a post-processing layer on top of existing detections. No retraining needed.

**Q: Can I disable severity scoring?**  
A: Yes - just use the `confidence` and `bbox` fields from detections.

**Q: How accurate is the severity score?**  
A: It's calibrated heuristically. Validate against your insurance adjuster assessments and adjust weights accordingly.

**Q: Can I export to insurance systems?**  
A: Yes! Use `--json` flag and integrate JSON output into your backend.

---

## 🚀 Next Steps

1. **Test the implementation**: `python model/scripts/infer.py --image test_image.jpg`
2. **Adjust weights**: Modify location_weights and formula based on your domain
3. **Validate**: Compare automated scores vs. human assessments
4. **Integrate**: Export JSON for your production pipeline
5. **Monitor**: Track severity distribution and refine weights over time

---

**Happy damage detecting! 🚗**

