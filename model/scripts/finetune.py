#!/usr/bin/env python3
"""
Fine-tune a pre-trained YOLOv11 model on your damage detection dataset.

Fine-tuning uses a lower learning rate and starts from best.pt weights
to preserve learned features while adapting to new data or improving performance.

Usage:
    python model/scripts/finetune.py --epochs 10 --batch 16 --lr 1e-4
    python model/scripts/finetune.py --weights model/weights/best_run2.pt --epochs 20 --imgsz 640
"""

import argparse
import os
from pathlib import Path
from ultralytics import YOLO


def finetune(
    weights="model/weights/best_run2.pt",
    data="data/raw/data.yaml",
    epochs=10,
    batch_size=16,
    imgsz=416,
    device="mps",  # Set to 0 for CUDA GPU, 'cpu' for CPU
    lr0=1e-4,
    patience=3,
    amp=True,
    workers=4,
):
    """
    Fine-tune YOLOv11 model.

    Args:
        weights: Path to pre-trained weights (best.pt or last.pt)
        data: Path to data.yaml
        epochs: Number of epochs to train
        batch_size: Batch size
        imgsz: Input image size
        device: Device ('mps', 0 for CUDA, 'cpu')
        lr0: Initial learning rate (lower for fine-tuning)
        patience: Early stopping patience (epochs with no improvement)
        amp: Use automatic mixed precision
        workers: Number of data loader workers
    """
    print(f"\n{'='*60}")
    print(f"  Fine-tuning YOLOv11 Damage Detector")
    print(f"{'='*60}")
    print(f"  Weights:   {weights}")
    print(f"  Dataset:   {data}")
    print(f"  Epochs:    {epochs}")
    print(f"  Batch:     {batch_size}")
    print(f"  Image sz:  {imgsz}")
    print(f"  Device:    {device}")
    print(f"  LR:        {lr0}")
    print(f"  AMP:       {amp}")
    print(f"{'='*60}\n")

    # Check weights exist
    if not os.path.exists(weights):
        print(f"❌ Error: Weights not found at {weights}")
        print(f"   Available weights:")
        weights_dir = "model/weights"
        if os.path.exists(weights_dir):
            for f in os.listdir(weights_dir):
                print(f"      - {f}")
        return

    # Load model
    model = YOLO(weights)

    # Fine-tune: lower LR, early stopping, fewer epochs
    results = model.train(
        data=data,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        lr0=lr0,
        patience=patience,
        amp=amp,
        workers=workers,
        resume=False,  # Important: False for fine-tuning (not resuming)
        project="outputs/runs",
        name="finetune",
        exist_ok=False,  # Create new run folder
    )

    print(f"\n{'='*60}")
    print(f"  Fine-tuning complete!")
    print(f"  Results saved to: outputs/runs/finetune/")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fine-tune YOLOv11 model on car damage detection dataset"
    )
    parser.add_argument(
        "--weights",
        type=str,
        default="model/weights/best_run2.pt",
        help="Path to pre-trained weights",
    )
    parser.add_argument("--data", type=str, default="data/raw/data.yaml", help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=416, help="Image size")
    parser.add_argument(
        "--device", type=str, default="mps", help="Device (mps, 0 for GPU, cpu)"
    )
    parser.add_argument("--lr", type=float, default=1e-4, help="Initial learning rate")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")
    parser.add_argument("--no-amp", action="store_true", help="Disable AMP")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers")

    args = parser.parse_args()

    finetune(
        weights=args.weights,
        data=args.data,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        lr0=args.lr,
        patience=args.patience,
        amp=not args.no_amp,
        workers=args.workers,
    )
