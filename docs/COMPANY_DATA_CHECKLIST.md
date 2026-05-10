# Company Data Integration Checklist

## Step 1: Organize Company Images ✓
```bash
# Copy your company car images to a folder
mkdir -p data/company_raw
cp /path/to/company/images/* data/company_raw/

# Auto-split into train/val/test (70/20/10)
python model/scripts/prepare_company_data.py \
  --company-dir data/company_raw \
  --output data/company
```

**Result:** `data/company/train|val|test/images/` with empty `labels/` folders

---

## Step 2: Annotate with Labels ✓
You have 22 damage classes from your Roboflow dataset:

```
Front-Windscreen-Damage, Headlight-Damage, Major-Rear-Bumper-Dent,
Rear-windscreen-Damage, RunningBoard-Dent, Sidemirror-Damage,
Signlight-Damage, Taillight-Damage, bonnet-dent, doorouter-dent,
doorouter-scratch, fender-dent, front-bumper-dent, front-bumper-scratch,
medium-Bodypanel-Dent, paint-chip, paint-trace, pillar-dent,
quaterpanel-dent, rear-bumper-dent, rear-bumper-scratch, roof-dent
```

**Use one of these tools:**
- **Roboflow Studio** (recommended, cloud-based) → Export as YOLO
- **LabelImg** (local) → `pip install labelimg && labelimg data/company/train/images`
- **Makesense.ai** (browser, free)

**Format:** Each image gets a `.txt` file with bounding boxes in YOLO format:
```
<class_id> <x_center> <y_center> <width> <height>
```

---

## Step 3: Validate Labels (optional but recommended)
```bash
python model/scripts/prepare_company_data.py \
  --validate-labels data/company/train/labels
```

Expected output:
```
✓ Total label files: 250
✓ Files with errors: 0
✓ All labels are valid!
```

---

## Step 4: Merge Datasets
```bash
# Combine company data + Roboflow data (16,326 images)
python model/scripts/prepare_company_data.py \
  --merge \
  --company-dir data/company \
  --roboflow-dir data/raw \
  --output data/combined
```

**Result:** `data/combined/train|val|test/` with mixed Roboflow + company images

---

## Step 5: Create data.yaml for Combined Dataset
```bash
cat > data/combined/data.yaml << 'EOF'
path: ../combined
train: train/images
val: val/images
test: test/images

nc: 22
names: ['Front-Windscreen-Damage', 'Headlight-Damage', 'Major-Rear-Bumper-Dent', 'Rear-windscreen-Damage', 'RunningBoard-Dent', 'Sidemirror-Damage', 'Signlight-Damage', 'Taillight-Damage', 'bonnet-dent', 'doorouter-dent', 'doorouter-scratch', 'fender-dent', 'front-bumper-dent', 'front-bumper-scratch', 'medium-Bodypanel-Dent', 'paint-chip', 'paint-trace', 'pillar-dent', 'quaterpanel-dent', 'rear-bumper-dent', 'rear-bumper-scratch', 'roof-dent']
EOF
```

---

## Step 6: Fine-tune Your Model
```bash
# RECOMMENDED: Fine-tune on combined data
python model/scripts/finetune.py \
  --epochs 15 \
  --batch 32 \
  --lr 1e-4 \
  --imgsz 640 \
  --device mps \
  --data data/combined/data.yaml
```

**Or use Python API:**
```python
from model.yolov11 import YOLOv11DamageDetector

detector = YOLOv11DamageDetector("model/weights/best_run2.pt")
detector.finetune(
    data_path="data/combined/data.yaml",
    epochs=15,
    batch_size=32,
    imgsz=640,
    lr0=1e-4
)
```

---

## Expected Timeline

- **Company images: 100-500** images
  - Annotate: 2-8 hours (or upload to Roboflow Studio, ~1-2 hours)
  - Fine-tune: 30 mins - 2 hours (M1 Pro with AMP)

- **Company images: 500-1000** images
  - Annotate: 5-20 hours
  - Fine-tune: 1-3 hours

- **Company images: 1000+** images
  - Annotate: 20+ hours
  - Fine-tune: 3-6 hours

---

## How to Annotate Faster

### Option 1: Roboflow Studio (fastest with ML assistance)
1. Upload company images to Roboflow
2. Use **Auto-Orient** + **Smart Polygon** annotation tools
3. Roboflow ML can pre-annotate (then you review)
4. Export as YOLO format

### Option 2: Pre-annotate with current model
```python
from model.yolov11 import YOLOv11DamageDetector

detector = YOLOv11DamageDetector("model/weights/best_run2.pt")

# Run inference to get rough boxes (you review + refine)
for img in Path("data/company/train/images").glob("*.jpg"):
    detections, _ = detector.predict(str(img), conf=0.3)
    # Convert detections → YOLO format labels
```

This gives you ~70% labeled, then you manually fix remaining 30%.

---

## Size of Datasets After Merging

**Roboflow (original):**
- Train: ~11,500 images
- Val: ~2,500 images  
- Test: ~2,300 images

**After adding 500 company images (70/20/10 split):**
- Train: ~11,850 images (~350 company)
- Val: ~2,600 images (~100 company)
- Test: ~2,350 images (~50 company)

**Result:** ~2-3% domain-specific data helps model adapt to your company's car types/angles/lighting.

---

## One-Liner Commands

```bash
# Organize
python model/scripts/prepare_company_data.py --company-dir /path/to/images --output data/company

# Merge
python model/scripts/prepare_company_data.py --merge --company-dir data/company --roboflow-dir data/raw --output data/combined

# Fine-tune
python model/scripts/finetune.py --epochs 15 --batch 32 --lr 1e-4 --data data/combined/data.yaml
```

---

## Result
✓ Model fine-tuned on both Roboflow + company data  
✓ Better performance on your company's specific car damage patterns  
✓ Saved to `outputs/runs/finetune/weights/best.pt`  

Deploy this model in production!
