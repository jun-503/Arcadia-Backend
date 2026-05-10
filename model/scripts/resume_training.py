#!/usr/bin/env python3
"""
Resume interrupted training from last.pt checkpoint.

Use this to continue training if your session was interrupted.
Last.pt contains the weights from the last epoch, so you can resume
from where you left off.

Usage:
    python model/scripts/resume_training.py --epochs 50
"""

import argparse
import os
from ultralytics import YOLO


def resume_training(
    weights="last.pt",
    epochs=50,
    device="mps",
    batch_size=16,
    imgsz=416,
    amp=True,
    workers=4,
):
    """
    Resume training from last.pt checkpoint.

    Args:
        weights: Path to last.pt (last checkpoint)
        epochs: Target total epochs (training continues from previous epoch)
        device: Device ('mps', 0 for CUDA, 'cpu')
        batch_size: Batch size
        imgsz: Input image size
        amp: Use automatic mixed precision
        workers: Number of data loader workers
    """
    print(f"\n{'='*60}")
    print(f"  Resuming YOLOv11 Training")
    print(f"{'='*60}")
    print(f"  Checkpoint:  {weights}")
    print(f"  Target eps:  {epochs}")
    print(f"  Device:      {device}")
    print(f"  Batch:       {batch_size}")
    print(f"  Image sz:    {imgsz}")
    print(f"  AMP:         {amp}")
    print(f"{'='*60}\n")

    # Load model from last checkpoint
    model = YOLO(weights)

    # Resume training
    results = model.train(
        epochs=epochs,
        device=device,
        batch=batch_size,
        imgsz=imgsz,
        amp=amp,
        workers=workers,
        resume=True,  # Key: resume=True to continue from checkpoint
    )

    print(f"\n{'='*60}")
    print(f"  Training resumed and completed!")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume interrupted YOLOv11 training")
    parser.add_argument(
        "--weights", type=str, default="last.pt", help="Path to last.pt checkpoint"
    )
    parser.add_argument("--epochs", type=int, default=50, help="Target total epochs")
    parser.add_argument(
        "--device", type=str, default="mps", help="Device (mps, 0 for GPU, cpu)"
    )
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=416, help="Image size")
    parser.add_argument("--no-amp", action="store_true", help="Disable AMP")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers")

    args = parser.parse_args()

    resume_training(
        weights=args.weights,
        epochs=args.epochs,
        device=args.device,
        batch_size=args.batch,
        imgsz=args.imgsz,
        amp=not args.no_amp,
        workers=args.workers,
    )
