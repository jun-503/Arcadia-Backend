#!/usr/bin/env python3
"""
Quick reference for fine-tuning with company data.

Your current setup:
  ✓ Roboflow dataset: 16,326 images × 22 damage classes
  ✓ Best model: model/weights/best_run2.pt
  ✓ Scripts ready: prepare_company_data.py, finetune.py

New: You have company car images from a company!

WORKFLOW:
  1. Organize company images (70/20/10 train/val/test split)
  2. Annotate with damage labels (same 22 classes)
  3. Merge company + Roboflow data
  4. Fine-tune your model
  5. Deploy improved model

TIME TO PRODUCTION: 1-3 weeks (depending on annotation speed)
"""

print(__doc__)

# Your 22 damage classes
CLASSES = {
    0: "Front-Windscreen-Damage",
    1: "Headlight-Damage",
    2: "Major-Rear-Bumper-Dent",
    3: "Rear-windscreen-Damage",
    4: "RunningBoard-Dent",
    5: "Sidemirror-Damage",
    6: "Signlight-Damage",
    7: "Taillight-Damage",
    8: "bonnet-dent",
    9: "doorouter-dent",
    10: "doorouter-scratch",
    11: "fender-dent",
    12: "front-bumper-dent",
    13: "front-bumper-scratch",
    14: "medium-Bodypanel-Dent",
    15: "paint-chip",
    16: "paint-trace",
    17: "pillar-dent",
    18: "quaterpanel-dent",
    19: "rear-bumper-dent",
    20: "rear-bumper-scratch",
    21: "roof-dent",
}

print("\nYour 22 Damage Classes:")
print("-" * 60)
for cid, name in CLASSES.items():
    print(f"  {cid:2d} → {name}")

print("\n" + "=" * 60)
print("QUICK START: 3 Steps to Fine-tune")
print("=" * 60)

commands = [
    {
        "step": 1,
        "title": "Organize Company Images",
        "cmd": "python model/scripts/prepare_company_data.py --company-dir /path/to/company/images --output data/company",
        "time": "5 min",
    },
    {
        "step": 2,
        "title": "Annotate with Labels (or skip + use auto-annotation)",
        "cmd": "labelimg data/company/train/images  # or use Roboflow Studio",
        "time": "2-8 hours (depends on # images)",
    },
    {
        "step": 3,
        "title": "Merge & Fine-tune",
        "cmd": """python model/scripts/prepare_company_data.py --merge \\
  --company-dir data/company \\
  --roboflow-dir data/raw \\
  --output data/combined

python model/scripts/finetune.py \\
  --epochs 15 \\
  --batch 32 \\
  --lr 1e-4 \\
  --data data/combined/data.yaml""",
        "time": "1-2 hours (M1 Pro)",
    },
]

for cmd_info in commands:
    print(f"\n[STEP {cmd_info['step']}] {cmd_info['title']}")
    print(f"Time: ~{cmd_info['time']}")
    print(f"\nCommand:\n  {cmd_info['cmd']}\n")

print("=" * 60)
print("RESULTS")
print("=" * 60)
print("""
outputs/runs/finetune/
├── weights/
│   ├── best.pt              ← Use this for production! ✨
│   └── last.pt
├── results.csv              ← mAP, loss curves
└── plots/
    ├── results.png
    └── confusion_matrix.png

Check: 
  - open outputs/runs/finetune/results/results.png  (training curves)
  - ls outputs/runs/finetune/val_batch*.jpg        (sample predictions)
""")

print("=" * 60)
print("FAQ")
print("=" * 60)
print("""
Q: How many company images do I need?
A: 100+ is good for fine-tuning. 500+ is excellent.

Q: Do I have to manually annotate?
A: Not entirely! Options:
   - Use your current model to pre-annotate (then review)
   - Upload to Roboflow Studio for ML-assisted annotation
   - Use free tools like LabelImg or Makesense.ai

Q: What if company images look very different from Roboflow?
A: Perfect! That's exactly when fine-tuning helps. Use progressive
   training (train on Roboflow first, then company data).

Q: Can I skip merging and fine-tune only on company data?
A: Only if you have 500+ company images. Otherwise, merge to preserve
   general knowledge and avoid overfitting.

Q: How fast is M1 Pro vs Colab T4 for fine-tuning?
A: M1 Pro: ~1-2 hours (AMP enabled)
   Colab T4: ~30-45 mins (but session limits)
   For fine-tuning, M1 Pro is more convenient (no upload/download).
""")

print("\n" + "=" * 60)
print("NEXT STEPS")
print("=" * 60)
print("""
1. Collect company car images → data/company_raw/
2. Run: python model/scripts/prepare_company_data.py --organize
3. Annotate (LabelImg or Roboflow Studio)
4. Run: python model/scripts/prepare_company_data.py --merge
5. Run: python model/scripts/finetune.py --data data/combined/data.yaml
6. Deploy: cp outputs/runs/finetune/weights/best.pt model/weights/

See docs/FINETUNING_WITH_COMPANY_DATA.md for detailed guide!
See docs/COMPANY_DATA_CHECKLIST.md for step-by-step checklist!
""")

print("=" * 60 + "\n")
