# Fine-tuning with Company Data

Your Roboflow dataset has **16,326 images** across **22 damage classes**. This guide shows how to integrate new company car images and fine-tune your model.

## Overview

### Scenario: You have company images (new data)
- **Stage 1:** Organize company images
- **Stage 2:** Annotate with damage labels (if needed)
- **Stage 3:** Merge with Roboflow data
- **Stage 4:** Fine-tune model

---

## Quick Decision Tree

**Do you have:**

```
├─ Images only (no labels)?
│  └─→ Go to "STAGE 1: Organize Company Images"
│
├─ Images + manual YOLO annotations (.txt files)?
│  └─→ Go to "STAGE 2: Validate Labels" (verify format)
│      └─→ Go to "STAGE 3: Merge Datasets"
│
├─ Images + bounding boxes from another tool?
│  └─→ Go to "Convert Labels" (see below)
│
└─ Just want to fine-tune on Roboflow data?
   └─→ Skip to "STAGE 4: Fine-tune" (at bottom)
```

---

## STAGE 1: Organize Company Images (auto-split 70/20/10)

If you have company car images but no labels yet:

### Step 1.1: Copy images to a folder
```bash
# Example: Create a folder with all company car images
mkdir -p data/company_raw
# Copy all .jpg/.png files here
cp /path/to/company/car/images/* data/company_raw/
```

### Step 1.2: Auto-split into train/val/test
```bash
python model/scripts/prepare_company_data.py \
  --company-dir data/company_raw \
  --output data/company \
  --train-ratio 0.7 --val-ratio 0.2 --test-ratio 0.1
```

**Output structure:**
```
data/company/
├── train/
│   ├── images/   (70% of images)
│   └── labels/   (empty - to be annotated)
├── val/
│   ├── images/   (20% of images)
│   └── labels/
└── test/
    ├── images/   (10% of images)
    └── labels/
```

---

## STAGE 2: Annotate Images with Damage Labels

You need to label company images with the **same 22 damage classes** as your Roboflow data.

### Option A: Use Roboflow Studio (easiest, cloud-based)
1. Go to [Roboflow](https://roboflow.com)
2. Create new project → Upload company images
3. Annotate using the web interface (bounding boxes + class labels)
4. Export as **YOLO format** → Downloads as `.zip`
5. Extract to `data/company/train/labels/`, `data/company/val/labels/`, etc.

### Option B: Use Local Annotation Tools
- **LabelImg** (simple, cross-platform)
  ```bash
  pip install labelimg
  labelimg data/company/train/images
  # Output: .txt files in YOLO format
  ```

- **Roboflow Annotate** (online)
- **CVAT** (advanced, self-hosted)
- **Makesense.ai** (browser-based, free)

### YOLO Label Format
Each image should have a corresponding `.txt` file with this format:
```
<class_id> <x_center> <y_center> <width> <height>
<class_id> <x_center> <y_center> <width> <height>
...
```

**Example:** For an image with 2 damage detections:
```
# 0 = Front-Windscreen-Damage, 5 = Sidemirror-Damage
0 0.45 0.32 0.15 0.25
5 0.82 0.55 0.08 0.12
```

**Your 22 classes (in order, 0-21):**
```
0 = Front-Windscreen-Damage
1 = Headlight-Damage
2 = Major-Rear-Bumper-Dent
3 = Rear-windscreen-Damage
4 = RunningBoard-Dent
5 = Sidemirror-Damage
6 = Signlight-Damage
7 = Taillight-Damage
8 = bonnet-dent
9 = doorouter-dent
10 = doorouter-scratch
11 = fender-dent
12 = front-bumper-dent
13 = front-bumper-scratch
14 = medium-Bodypanel-Dent
15 = paint-chip
16 = paint-trace
17 = pillar-dent
18 = quaterpanel-dent
19 = rear-bumper-dent
20 = rear-bumper-scratch
21 = roof-dent
```

---

## STAGE 3: Validate & Merge Datasets

### Step 3.1: Validate company labels (optional)
```bash
python model/scripts/prepare_company_data.py \
  --validate-labels data/company/train/labels
```

Output:
```
Validation Summary:
  Total label files: 250
  Files with errors: 0
  ✓ All labels are valid!
```

### Step 3.2: Merge company + Roboflow data
```bash
python model/scripts/prepare_company_data.py \
  --merge \
  --company-dir data/company \
  --roboflow-dir data/raw \
  --output data/combined
```

**Result: Combined dataset**
```
data/combined/
├── train/
│   ├── images/   (Roboflow train + Company train)
│   └── labels/
├── val/
│   ├── images/   (Roboflow val + Company val)
│   └── labels/
└── test/
    ├── images/   (Roboflow test + Company test)
    └── labels/
```

### Step 3.3: Create data.yaml for combined dataset
```bash
cat > data/combined/data.yaml << 'EOF'
path: ../combined
train: train/images
val: val/images
test: test/images

nc: 22
names: ['Front-Windscreen-Damage', 'Headlight-Damage', 'Major-Rear-Bumper-Dent', 
        'Rear-windscreen-Damage', 'RunningBoard-Dent', 'Sidemirror-Damage', 
        'Signlight-Damage', 'Taillight-Damage', 'bonnet-dent', 'doorouter-dent', 
        'doorouter-scratch', 'fender-dent', 'front-bumper-dent', 'front-bumper-scratch', 
        'medium-Bodypanel-Dent', 'paint-chip', 'paint-trace', 'pillar-dent', 
        'quaterpanel-dent', 'rear-bumper-dent', 'rear-bumper-scratch', 'roof-dent']
EOF
```

---

## STAGE 4: Fine-tune Model with Company Data

### Option A: Fine-tune on combined dataset (Roboflow + Company) — RECOMMENDED
```bash
python model/scripts/finetune.py \
  --epochs 15 \
  --batch 32 \
  --lr 1e-4 \
  --imgsz 640 \
  --data data/combined/data.yaml
```

**Expected results:**
- Faster convergence (good transfer learning)
- Better performance on company cars (domain-specific)
- ~1-2 hours on M1 Pro with AMP + batch=32

### Option B: Fine-tune on company data only (if company data is large)
```bash
python model/scripts/finetune.py \
  --epochs 20 \
  --batch 16 \
  --lr 5e-4 \
  --imgsz 640 \
  --data data/company/data.yaml
```

⚠️ **Warning:** This can lead to overfitting if company data is small (<500 images).

### Option C: Progressive fine-tuning (best for domain shift)
```bash
# Step 1: Fine-tune on Roboflow only (preserve general knowledge)
python model/scripts/finetune.py \
  --epochs 10 \
  --batch 16 \
  --lr 1e-4 \
  --data data/raw/data.yaml

# Step 2: Fine-tune on combined (adapt to company cars)
python model/scripts/finetune.py \
  --epochs 10 \
  --batch 16 \
  --lr 5e-5 \
  --data data/combined/data.yaml
```

---

## Monitoring & Results

Fine-tuning outputs saved to:
```
outputs/runs/finetune/
├── weights/
│   ├── best.pt         ← Use this for production
│   └── last.pt
├── results.csv         ← Metrics (mAP, loss, etc.)
└── plots/
    ├── results.png     ← Training curves
    ├── confusion_matrix.png
    └── val_*.jpg       ← Sample predictions
```

### Check results:
```bash
# View training curves
open outputs/runs/finetune/results/results.png

# View validation examples
ls outputs/runs/finetune/val_batch*.jpg
```

### Compare models:
```python
from model.yolov11 import YOLOv11DamageDetector

# Test on same image
test_img = "test_car.jpg"

# Original model
detector_old = YOLOv11DamageDetector("model/weights/best_run2.pt")
results_old = detector_old.predict(test_img)

# Fine-tuned model
detector_new = YOLOv11DamageDetector("outputs/runs/finetune/weights/best.pt")
results_new = detector_new.predict(test_img)

print(f"Old detections: {len(results_old[0].boxes)}")
print(f"New detections: {len(results_new[0].boxes)}")
```

---

## Common Issues & Solutions

### Q: I have bounding boxes but in different format (e.g., COCO, Pascal VOC)?

**Convert to YOLO format:**

```python
# COCO format (x_min, y_min, width, height) → YOLO format
def coco_to_yolo(x_min, y_min, width, height, img_width, img_height):
    x_center = (x_min + width / 2) / img_width
    y_center = (y_min + height / 2) / img_height
    w = width / img_width
    h = height / img_height
    return x_center, y_center, w, h

# Pascal VOC format (x_min, y_min, x_max, y_max) → YOLO format
def voc_to_yolo(x_min, y_min, x_max, y_max, img_width, img_height):
    x_center = (x_min + x_max) / 2 / img_width
    y_center = (y_min + y_max) / 2 / img_height
    w = (x_max - x_min) / img_width
    h = (y_max - y_min) / img_height
    return x_center, y_center, w, h
```

### Q: How many company images do I need?

- **100-200 images:** Good start for fine-tuning (merge with Roboflow)
- **500+ images:** Can fine-tune independently
- **2000+ images:** Consider training from scratch for best results

### Q: My company data looks very different from Roboflow data (different lighting, angles, car models)?

→ This is **good!** Fine-tuning will help adapt to your domain. Use `data/combined/` with progressive training (Option C above).

### Q: Should I freeze backbone layers for faster training?

Advanced option — requires custom training loop. For now, use lower `--lr` (1e-4 to 1e-5) to prevent forgetting.

---

## Summary Workflow

```
1. ✓ Have company car images
   ↓
2. python prepare_company_data.py --organize
   ↓
3. Annotate with damage labels (LabelImg, Roboflow, etc.)
   ↓
4. python prepare_company_data.py --merge
   ↓
5. python model/scripts/finetune.py --data data/combined/data.yaml
   ↓
6. ✓ Fine-tuned model ready in outputs/runs/finetune/weights/best.pt
```

---

## Next Steps

1. **Organize company images:** `python model/scripts/prepare_company_data.py --company-dir <path> --output data/company`
2. **Annotate** (if needed): Use LabelImg or Roboflow
3. **Merge & fine-tune:** `python model/scripts/finetune.py --data data/combined/data.yaml --epochs 15`
4. **Evaluate:** Check `outputs/runs/finetune/results.png` and test on company test set
5. **Deploy:** Copy `outputs/runs/finetune/weights/best.pt` to production

Questions? Let me know!
