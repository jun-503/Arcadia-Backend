# Severity Scoring Documentation Index

## 🎯 Quick Start (5 minutes)

1. **Read this first**: [`SEVERITY_QUICK_REF.md`](SEVERITY_QUICK_REF.md) - 2-minute overview
2. **Run inference**: `python model/scripts/infer.py --image path/to/car.jpg`
3. **See results**: Check `outputs/predictions/`
4. **Export JSON**: Add `--json` flag for detailed export

---

## 📚 Documentation

### For Getting Started
- **[`SEVERITY_QUICK_REF.md`](SEVERITY_QUICK_REF.md)** ⭐ START HERE
  - TL;DR overview
  - What changed
  - Running commands
  - FAQ

### For Understanding the System
- **[`docs/SEVERITY_SCORING.md`](docs/SEVERITY_SCORING.md)** 📖 COMPREHENSIVE GUIDE
  - Complete methodology
  - Scoring formula with examples
  - Output examples (console, JSON, images)
  - Customization options
  - Integration patterns

### For Implementation Details
- **[`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)** 🔧 TECHNICAL DEEP DIVE
  - What was added/modified
  - Formula breakdown
  - All customization options
  - Testing guide
  - Use cases

### For Before/After Understanding
- **[`BEFORE_AFTER.md`](BEFORE_AFTER.md)** 🔄 COMPARISON GUIDE
  - Before/after output comparison
  - Dictionary structure changes
  - Image annotation differences
  - Business logic impact
  - Customization capabilities

---

## 🚀 Quick Commands

```bash
# Basic inference (prints to console)
python model/scripts/infer.py --image car.jpg

# Save results as JSON
python model/scripts/infer.py --image car.jpg --json

# Custom confidence threshold
python model/scripts/infer.py --image car.jpg --conf 0.5 --json

# Use different model weights
python model/scripts/infer.py --image car.jpg --weights model/weights/yolo11n.pt

# Run Python demo
python model/scripts/demo_severity.py
```

---

## 📊 Severity Levels Quick Reference

| Level | Score | Color | Meaning |
|-------|-------|-------|---------|
| **LOW** | 0-20 | 🟢 | Minimal damage |
| **MEDIUM** | 20-50 | 🟡 | Moderate damage |
| **HIGH** | 50-75 | 🟠 | Significant damage |
| **CRITICAL** | 75-100 | 🔴 | Severe damage |

---

## 💡 Common Use Cases

### Insurance Claims
- Export JSON with `--json` flag
- Use `average_severity` for cost estimation
- Use `severity_level` for routing

### Mobile App Integration
- Display color-coded boxes (🟢/🟡/🟠/🔴)
- Show severity breakdown charts
- Export reports as PDF

### Data Analysis
- Track damage type trends
- Identify high-damage vehicle parts
- Compare model vs. adjuster assessments

### Fine-tuning
- Use severity to weight training samples
- Focus on high-severity misclassifications
- Improve detection of critical parts (windscreen, lights)

---

## 📁 Modified Files

- **`model/yolov11.py`** - Added severity scoring
- **`model/scripts/infer.py`** - Enhanced output and JSON export
- **`model/scripts/demo_severity.py`** - NEW: Demo script
- **`docs/SEVERITY_SCORING.md`** - NEW: Comprehensive guide
- **`SEVERITY_QUICK_REF.md`** - NEW: Quick reference
- **`IMPLEMENTATION_SUMMARY.md`** - NEW: Technical details
- **`BEFORE_AFTER.md`** - NEW: Comparison guide

---

## 🔧 Customization Levels

### Level 1: Location Weights (Easiest)
Adjust how much different car parts impact severity.

Edit in `model/yolov11.py`:
```python
location_weights = {
    'windscreen': 1.5,  # Increase = more severe
    'bumper': 1.3,
    'paint': 0.6,       # Decrease = less severe
}
```

### Level 2: Severity Thresholds (Medium)
Change what score maps to which level.

Edit in `model/yolov11.py`:
```python
if combined_severity < 20:      # ← Change these values
    severity_level = "LOW"
elif combined_severity < 50:
    severity_level = "MEDIUM"
```

### Level 3: Scoring Formula (Advanced)
Change how components are weighted.

Edit in `model/yolov11.py`:
```python
combined_severity = (
    area_severity * 0.5 +           # Area weight
    confidence_severity * 0.3 +     # Confidence weight
    (confidence_severity * location_weight) * 0.2  # Location weight
)
```

---

## 📋 Sample Outputs

### Console Output
```
DETECTIONS (2 damages found):
──────────────────────────────────────────────────────────────────────

1. FRONT-BUMPER-DENT
   Confidence:           0.789 (78.9/100)
   Area:                 12.45% of image (42.3/100 severity)
   Location Weight:      1.30x
   ➜ COMBINED SEVERITY:  62.5/100 [HIGH]
   BBox:                 (37, 45) → (554, 459)
```

### JSON Export
```json
{
  "total_damages": 2,
  "average_severity": 48.4,
  "severity_assessment": "MODERATE",
  "detections": [
    {
      "class": "front-bumper-dent",
      "combined_severity": 62.5,
      "severity_level": "HIGH",
      "area_percent": 12.45,
      "location_weight": 1.3
    }
  ]
}
```

### Annotated Image
- Color-coded bounding boxes (🟢/🟡/🟠/🔴)
- Main label: `ClassName | Confidence | SeverityLevel (Score)`
- Secondary info: `Area: X% | Loc Weight: Y.Zx`

---

## ❓ FAQ

**Q: Do I need to retrain the model?**  
A: No. Severity scoring is post-processing, not part of model training.

**Q: Can I disable severity scoring?**  
A: Yes - just use the `confidence` and `bbox` fields from detections.

**Q: Is it production-ready?**  
A: Yes - all calculations are local, no external dependencies, fully customizable.

**Q: How do I integrate with my backend?**  
A: Export JSON with `--json` flag and parse in your backend system.

**Q: Can I validate against human assessments?**  
A: Yes - compare `average_severity` with adjuster scores and adjust weights.

---

## �� Learning Path

1. **Beginner**: Read [`SEVERITY_QUICK_REF.md`](SEVERITY_QUICK_REF.md) (5 min)
2. **User**: Run commands and check [`BEFORE_AFTER.md`](BEFORE_AFTER.md) (10 min)
3. **Developer**: Study [`docs/SEVERITY_SCORING.md`](docs/SEVERITY_SCORING.md) (20 min)
4. **Expert**: Review [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) (30 min)
5. **Customizer**: Modify scores in `model/yolov11.py` (varies)

---

## 📞 Support

- Check FAQs in [`SEVERITY_QUICK_REF.md`](SEVERITY_QUICK_REF.md)
- Review examples in [`docs/SEVERITY_SCORING.md`](docs/SEVERITY_SCORING.md)
- See troubleshooting in [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)
- Run demo: `python model/scripts/demo_severity.py`

---

**Ready to start? Run:**
```bash
python model/scripts/infer.py --image path/to/your/car.jpg
```

