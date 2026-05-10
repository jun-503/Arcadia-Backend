# Documentation Index

Complete technical documentation for the YOLOv11 Car Damage Detection system with Severity Scoring.

## 📚 Documentation Files

### 1. **TECHNICAL_INTERNALS.md** 🔧 START HERE FOR TECHNICAL DETAILS
   - **What it covers:** Deep technical explanation of every calculation
   - **Best for:** Developers who want to understand the math
   - **Contents:**
     - Detection flow (step-by-step)
     - Confidence calculation and extraction
     - Area calculation (pixel → percentage → severity)
     - Location weighting system
     - Complete severity scoring formula
     - Severity classification thresholds
     - Visualization process
     - JSON export structure
     - Mathematical formulas with notation
     - Weight distribution analysis
     - Performance characteristics
     - Error handling & edge cases
     - Testing & validation examples
     - Debugging guide

### 2. **VISUAL_FLOWCHARTS.md** 📊 FOR VISUAL LEARNERS
   - **What it covers:** ASCII flowcharts and diagrams
   - **Best for:** Visual understanding of data flow
   - **Contents:**
     - Complete processing pipeline
     - Area severity calculation flow
     - Confidence conversion diagram
     - Location weight matching flow
     - Combined severity formula breakdown
     - Severity classification decision tree
     - Vehicle-level assessment flow
     - JSON export structure tree
     - Visualization layers
     - Data flow from detection to decision
     - Performance timeline

### 3. **SEVERITY_SCORING.md** 📖 COMPREHENSIVE GUIDE
   - **What it covers:** Full explanation with examples
   - **Best for:** Understanding the complete system
   - **Contents:**
     - Overview of severity scoring
     - Methodology (3 components)
     - Component weights explanation
     - Combined severity formula
     - Output examples (console, JSON, images)
     - Usage examples (Python API, command line)
     - Customization guide (3 levels)
     - Integration patterns
     - FAQ

## 🎯 Quick Navigation

### I want to understand...

**How area severity is calculated**
- → `TECHNICAL_INTERNALS.md` → "Area Calculation" section
- → `VISUAL_FLOWCHARTS.md` → "Area Severity Calculation Flow"

**How confidence is converted to severity**
- → `TECHNICAL_INTERNALS.md` → "Confidence Calculation" section
- → `VISUAL_FLOWCHARTS.md` → "Confidence Conversion Flow"

**How location weights work**
- → `TECHNICAL_INTERNALS.md` → "Location Weighting" section
- → `VISUAL_FLOWCHARTS.md` → "Location Weight Matching Flow"

**The complete severity formula**
- → `TECHNICAL_INTERNALS.md` → "Severity Scoring" section
- → `TECHNICAL_INTERNALS.md` → "Mathematical Formulas" section
- → `VISUAL_FLOWCHARTS.md` → "Combined Severity Formula Breakdown"

**The complete pipeline**
- → `VISUAL_FLOWCHARTS.md` → "Complete Processing Pipeline"
- → `TECHNICAL_INTERNALS.md` → "Detection Flow"

**How to customize the system**
- → `SEVERITY_SCORING.md` → "Customization" section
- → `TECHNICAL_INTERNALS.md` → "Weight Distribution Analysis"

**Examples of calculations**
- → `TECHNICAL_INTERNALS.md` → "Complete Example Calculation"
- → `VISUAL_FLOWCHARTS.md` → "Combined Severity Formula Breakdown"

**What the outputs look like**
- → `SEVERITY_SCORING.md` → "Output Examples"
- → `VISUAL_FLOWCHARTS.md` → "JSON Export Structure"

**Testing & validation**
- → `TECHNICAL_INTERNALS.md` → "Validation & Testing"
- → `TECHNICAL_INTERNALS.md` → "Debugging Guide"

## 🔄 Reading Sequences

### For Data Scientists
1. Start: `VISUAL_FLOWCHARTS.md` (5 min)
2. Details: `TECHNICAL_INTERNALS.md` (20 min)
3. Formulas: `TECHNICAL_INTERNALS.md` → "Mathematical Formulas"
4. Customization: `SEVERITY_SCORING.md` → "Customization"

### For Backend Developers
1. Start: `TECHNICAL_INTERNALS.md` → "JSON Export" (5 min)
2. Structure: `VISUAL_FLOWCHARTS.md` → "JSON Export Structure"
3. Integration: `SEVERITY_SCORING.md` → "Integration with Insurance/Business Systems"
4. Testing: `TECHNICAL_INTERNALS.md` → "Validation & Testing"

### For DevOps/Infrastructure
1. Start: `TECHNICAL_INTERNALS.md` → "Performance Characteristics" (5 min)
2. Timeline: `VISUAL_FLOWCHARTS.md` → "Performance Timeline"
3. Edge Cases: `TECHNICAL_INTERNALS.md` → "Error Handling & Edge Cases"
4. Optimization: `TECHNICAL_INTERNALS.md` → Performance section

### For Product/Business
1. Start: `SEVERITY_SCORING.md` → "Use Cases" (5 min)
2. Examples: `SEVERITY_SCORING.md` → "Output Examples"
3. Custom: `SEVERITY_SCORING.md` → "Customization"

## 📋 Key Concepts Explained

### Confidence Score
- **What:** Model's probability that damage exists (0-1)
- **From:** YOLO detection head
- **Used for:** 30% weight in severity calculation
- **Found in:** `TECHNICAL_INTERNALS.md` → "Confidence Calculation"

### Area Severity
- **What:** Damage size as % of image, mapped to 0-100 scale
- **Calculation:** 4 tiered thresholds for non-linear mapping
- **Used for:** 50% weight in severity calculation (most important)
- **Found in:** `TECHNICAL_INTERNALS.md` → "Area Calculation"

### Location Weight
- **What:** Multiplier based on car part (0.6x to 1.5x)
- **Why:** Windscreen damage > paint chip (same size)
- **Used for:** 20% weight in severity calculation
- **Found in:** `TECHNICAL_INTERNALS.md` → "Location Weighting"

### Combined Severity
- **What:** Final severity score (0-100)
- **Formula:** (Area×0.5) + (Confidence×0.3) + (Confidence×Weight×0.2)
- **Output:** Used for classification and decision-making
- **Found in:** `TECHNICAL_INTERNALS.md` → "Severity Scoring"

### Severity Level
- **What:** Categorical classification (LOW/MEDIUM/HIGH/CRITICAL)
- **Thresholds:** < 20 / 20-50 / 50-75 / 75+
- **Output:** Used for visualization and business logic
- **Found in:** `TECHNICAL_INTERNALS.md` → "Severity Classification"

## 🔢 Math Reference

For mathematical formulas and notation, see:
- `TECHNICAL_INTERNALS.md` → "Mathematical Formulas" section
- Includes LaTeX notation for all calculations
- Complete derivations and examples

## 🛠️ Practical Examples

### Step-by-step calculation example
- `TECHNICAL_INTERNALS.md` → "Complete Example Calculation"
- Real numbers from actual detection
- Shows all intermediate steps

### Weight distribution scenarios
- `TECHNICAL_INTERNALS.md` → "Weight Distribution Analysis"
- Examples for insurance, safety, accuracy-focused use cases

### Visual examples
- `VISUAL_FLOWCHARTS.md` → Multiple examples in each section
- ASCII diagrams showing data flow

## ⚙️ Customization Guide

To modify any part of the system:

1. **Change location weights**
   → `TECHNICAL_INTERNALS.md` → "Location Weighting"
   → Edit `model/yolov11.py` location_weights dict

2. **Change severity thresholds**
   → `TECHNICAL_INTERNALS.md` → "Severity Classification"
   → Edit `model/yolov11.py` threshold values

3. **Change weight distribution**
   → `TECHNICAL_INTERNALS.md` → "Weight Distribution Analysis"
   → Edit `model/yolov11.py` formula coefficients

4. **Change area mapping**
   → `TECHNICAL_INTERNALS.md` → "Area Calculation"
   → Edit `model/yolov11.py` tiered thresholds

## 📊 File Structure Reference

```
docs/
├── README.md                      # This file (index)
├── TECHNICAL_INTERNALS.md         # Deep technical details
├── VISUAL_FLOWCHARTS.md           # ASCII diagrams & flows
└── SEVERITY_SCORING.md            # Comprehensive guide (one level up)

Related files:
├── SEVERITY_QUICK_REF.md          # Quick reference
├── IMPLEMENTATION_SUMMARY.md      # What was changed
└── BEFORE_AFTER.md                # Comparison with baseline
```

## 🚀 Getting Started

1. **Run inference first:** `python model/scripts/infer.py --image car.jpg`
2. **Read SEVERITY_QUICK_REF.md** for 2-minute overview
3. **Pick a section** from this README based on your role
4. **Dive into the relevant documentation**

## 💡 Pro Tips

- Use `VISUAL_FLOWCHARTS.md` while reading `TECHNICAL_INTERNALS.md` for better understanding
- Search for keywords within files using your editor's find function
- Mathematical formulas in `TECHNICAL_INTERNALS.md` use LaTeX notation
- All examples are based on real car damage detection scenarios
- Flowcharts show actual data flow from image to decision

## ❓ Still Confused?

- Check the FAQs in `SEVERITY_SCORING.md`
- See debugging guide in `TECHNICAL_INTERNALS.md`
- Run the demo: `python model/scripts/demo_severity.py`
- Review examples in `BEFORE_AFTER.md`

---

**Last Updated:** April 21, 2026
**Version:** 1.0 (Initial Release)

