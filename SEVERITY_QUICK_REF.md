# Quick Reference: Severity Scoring

## TL;DR - What Changed

**Before:**
```
front-bumper-dent: 0.79 @ (37, 45, 554, 459)
```

**After:**
```
FRONT-BUMPER-DENT
  Confidence:           0.789 (78.9/100)
  Area:                 12.45% of image (42.3/100 severity)
  Location Weight:      1.30x
  ➜ COMBINED SEVERITY:  62.5/100 [HIGH]
  BBox:                 (37, 45) → (554, 459)

VEHICLE ASSESSMENT: Average severity 62.5/100 [HIGH]
```

---

## Run Inference Now

```bash
# Simple inference
python model/scripts/infer.py --image path/to/car.jpg

# Save JSON results
python model/scripts/infer.py --image path/to/car.jpg --json

# Custom confidence
python model/scripts/infer.py --image path/to/car.jpg --conf 0.5 --json
```

---

## Severity Levels

| Level | Score | Meaning |
|-------|-------|---------|
| 🟢 LOW | 0-20 | Minimal, mostly cosmetic |
| 🟡 MEDIUM | 20-50 | Noticeable, moderate repair |
| 🟠 HIGH | 50-75 | Significant, substantial repair |
| 🔴 CRITICAL | 75-100 | Severe, major repair/replacement |

---

## Scoring Components

### 1. Area (50% weight)
- How much of the image is damaged?
- 1% → 5 severity, 10% → 65 severity, 20%+ → 100 severity

### 2. Confidence (30% weight)
- How sure is the model?
- 0.5 confidence → 50 severity, 0.9 confidence → 90 severity

### 3. Location (20% weight)
- What part is damaged?
- Windscreen 1.5x, Bumper 1.3x, Paint 0.6x, etc.

**Formula:** `(Area × 0.5) + (Confidence × 0.3) + (Confidence × Weight × 0.2)`

---

## Python Usage

```python
from model.yolov11 import YOLOv11DamageDetector

detector = YOLOv11DamageDetector("best_run2.pt")
detections, img = detector.predict("car.jpg", visualize=True)

for det in detections:
    print(f"{det['class']}: {det['combined_severity']:.0f}/100 [{det['severity_level']}]")

img.save("result.jpg")
```

---

## JSON Output Structure

```json
{
  "total_damages": 2,
  "average_severity": 48.4,
  "severity_assessment": "MODERATE",
  "detections": [
    {
      "class": "front-bumper-dent",
      "confidence": 0.789,
      "combined_severity": 62.5,
      "severity_level": "HIGH",
      "area_percent": 12.45,
      "location_weight": 1.3
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

---

## Color-Coded Visualization

- 🟢 GREEN box = LOW severity
- 🟡 YELLOW box = MEDIUM severity
- 🟠 ORANGE box = HIGH severity
- 🔴 RED box = CRITICAL severity

Each box shows: `ClassName | Confidence | SeverityLevel (Score)`

---

## Output Files

```
outputs/predictions/
├── detection_20250421_143045.jpg    # Annotated image
└── detection_20250421_143045.json   # Detailed results (if --json used)
```

---

## Customization

### Change Location Weights
Edit `model/yolov11.py` line ~85:
```python
location_weights = {
    'windscreen': 1.5,  # ← Adjust
    'headlight': 1.4,
    'bumper': 1.3,
    ...
}
```

### Change Severity Thresholds
Edit `model/yolov11.py` line ~125:
```python
if combined_severity < 20:      # ← Change thresholds
    severity_level = "LOW"
elif combined_severity < 50:
    severity_level = "MEDIUM"
```

### Change Weight Distribution
Edit `model/yolov11.py` line ~120:
```python
combined_severity = (
    area_severity * 0.5 +           # ← Area (now 50%)
    confidence_severity * 0.3 +     # ← Confidence (now 30%)
    (confidence_severity * location_weight) * 0.2  # ← Location (now 20%)
)
```

---

## FAQ

**Q: Why is my small scratch marked HIGH severity?**  
A: Could be high confidence (model very sure) + critical part (windscreen) + location weight boost.

**Q: Can I disable severity scoring?**  
A: Use original `model/yolov11.py` from git history, or just use the `confidence` and `area_percent` fields.

**Q: How do I export for insurance systems?**  
A: Use `--json` flag and parse JSON output in your backend.

**Q: Can I adjust weights per customer?**  
A: Yes! Modify `location_weights` dict or formula weights before calling `predict()`.

