# YOLOv11 Car Damage Detection

Fine-grained damage detection on vehicles using YOLOv11 object detection.

## Project Structure

```
Project/
├── data/
│   └── raw/
│       ├── data.yaml              # YOLO dataset config
│       ├── train/                 # Training images & labels
│       ├── valid/                 # Validation images & labels
│       └── test/                  # Test images & labels
│
├── model/
│   ├── weights/
│   │   ├── yolo11n.pt             # Base YOLOv11 nano model
│   │   └── best_run2.pt           # Fine-tuned checkpoint (best weights)
│   ├── scripts/
│   │   ├── finetune.py            # Fine-tune pre-trained model
│   │   ├── resume_training.py     # Resume interrupted training
│   │   └── infer.py               # Run inference on images
│   └── yolov11.py                 # Core detector class
│
├── outputs/
│   ├── runs/                      # Training outputs (auto-created)
│   └── predictions/               # Inference results (auto-created)
│
├── README.md                      # This file
└── .gitignore
```

## Setup

### Prerequisites
- Python 3.8+
- PyTorch (with MPS support on M1 Pro or CUDA on GPU)

### Installation

```bash
# Clone or download project
cd Project

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install ultralytics
pip install ultralytics torch torchvision
```

## Usage

### 1. Fine-tune from Pre-trained Model

Fine-tuning uses lower learning rate and starts from `best_run2.pt` to preserve learned features.
**Fastest way to improve:** lower LR + fewer epochs.

```bash
# Fine-tune with default settings (10 epochs, lr=1e-4)
python model/scripts/finetune.py

# Custom settings
python model/scripts/finetune.py --epochs 20 --batch 32 --lr 1e-4 --imgsz 640

# Use different weights
python model/scripts/finetune.py --weights model/weights/yolo11n.pt --epochs 15
```

**What happens:**
- Loads `best_run2.pt`
- Trains with lr=1e-4 (10x lower than normal)
- Saves results to `outputs/runs/finetune/`
- Stops early if validation doesn't improve (patience=3)

### 2. Resume Interrupted Training

If training was interrupted, continue from `last.pt`:

```bash
python model/scripts/resume_training.py --epochs 50
```

### 3. Run Inference

Detect damage in images:

```bash
# Basic inference
python model/scripts/infer.py --image path/to/car.jpg

# Custom confidence threshold
python model/scripts/infer.py --image path/to/car.jpg --conf 0.5 --device mps

# Batch inference (multiple images)
python model/scripts/infer.py --image data/test/images/
```

Results saved to `outputs/predictions/`

### 4. Manual Training from Scratch

Using the Python API:

```python
from model.yolov11 import YOLOv11DamageDetector

# Initialize from base model
detector = YOLOv11DamageDetector(model_name="yolo11n.pt")

# Train from scratch (25 epochs)
detector.train(
    data_path="data/raw/data.yaml",
    epochs=25,
    batch_size=16,
    imgsz=416,
    device="mps"  # or 0 for CUDA GPU
)

# Fine-tune after training
detector.finetune(
    data_path="data/raw/data.yaml",
    epochs=10,
    batch_size=16,
    lr0=1e-4,
    device="mps"
)

# Evaluate
results = detector.evaluate(data_path="data/raw/data.yaml")

# Predict on single image
detections, output_img = detector.predict("test_car.jpg")
if output_img:
    output_img.save("test_car_output.jpg")
```

## Performance Tips

### Reduce Training Time

1. **Use fine-tuning** (not training from scratch)
   - Loads `best_run2.pt` with pre-trained features
   - Typical speedup: 3-5x faster convergence

2. **Mixed precision (AMP)**
   - Enabled by default in all scripts
   - Typical speedup: 1.5-3x on CUDA, ~1.2x on M1 MPS

3. **Increase batch size** (if memory allows)
   - `--batch 32` or `--batch 64` instead of 16
   - Better GPU utilization

4. **Reduce image size** (if accuracy allows)
   - `--imgsz 480` instead of 416 (4x faster, trade accuracy)
   - `--imgsz 640` for better accuracy (slower)

5. **Freeze backbone** (advanced)
   - Train only detection head for 5-10 epochs
   - Then unfreeze full model for fine-tune
   - Requires custom code (contact for details)

### Device Selection

| Device | Pros | Cons |
|--------|------|------|
| **M1 Pro (mps)** | Local, no upload, 32GB RAM, convenient | Slower than T4 for conv nets, MPS mixed precision less mature |
| **Colab T4 (GPU)** | ~2-3x faster, mature CUDA+AMP | Session limits (12h), upload/download friction |
| **CPU** | Works everywhere | Very slow (20-50x slower than GPU) |

**Recommendation:** Use M1 Pro for development/iteration. Run final/heavy training on Colab T4 if you need speed.

## Dataset Format

Expected YOLO format in `data/raw/`:

```
data/raw/
├── data.yaml          # Config file
├── train/
│   ├── images/        # .jpg files
│   └── labels/        # .txt (YOLO format: class x_center y_center width height)
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

**data.yaml** should contain:
```yaml
path: /absolute/or/relative/path/to/data
train: train/images
val: valid/images
test: test/images

nc: 22  # number of classes
names: ['Front-Windscreen-Damage', 'Headlight-Damage', ...]  # class names
```

## Key Files

- `model/yolov11.py` — Core YOLOv11DamageDetector class
- `model/scripts/finetune.py` — Fine-tuning script (recommended for quick improvements)
- `model/scripts/resume_training.py` — Resume from checkpoint if interrupted
- `model/scripts/infer.py` — Batch inference
- `model/weights/best_run2.pt` — Your best trained model
- `model/weights/yolo11n.pt` — Base YOLOv11 nano model

## Troubleshooting

### "Model not found"
```bash
ls -la model/weights/
# Check if best_run2.pt exists; use correct path in --weights
```

### Out of memory (OOM)
```bash
# Reduce batch size
python model/scripts/finetune.py --batch 8

# Reduce image size
python model/scripts/finetune.py --imgsz 320

# Use smaller model (if available)
# (Currently nano; micro/pico not common for this task)
```

### Slow training on M1 Pro
- MPS support is improving; ensure PyTorch 2.0+
- Consider Colab T4 for faster training (see Device Selection above)

## Next Steps

1. **Quick start:** `python model/scripts/finetune.py --epochs 5` (test run)
2. **Benchmark:** Run 1 epoch on both M1 Pro (mps) and Colab (cuda) to compare speed
3. **Deploy:** Use best model weights for inference in production

## References

- [YOLOv11 Docs](https://docs.ultralytics.com/models/yolov11/)
- [Ultralytics GitHub](https://github.com/ultralytics/ultralytics)
- [YOLO Dataset Format](https://docs.ultralytics.com/datasets/detect/)
