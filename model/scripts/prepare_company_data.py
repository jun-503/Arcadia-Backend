#!/usr/bin/env python3
"""
Prepare new company data for fine-tuning YOLOv11 damage detector.

This script helps you:
1. Organize company images into train/val/test splits
2. Generate YOLO format labels (if you have them)
3. Merge company data with Roboflow data
4. Create a new data.yaml for combined dataset

Usage:
    # Option 1: Organize company images (auto-split 70/20/10)
    python prepare_company_data.py --company-dir /path/to/company/images --output data/company

    # Option 2: Merge company data with Roboflow (for fine-tuning)
    python prepare_company_data.py --company-dir data/company --roboflow-dir data/raw \
                                    --merge --output data/combined

    # Option 3: Just validate labels (if you have them)
    python prepare_company_data.py --validate-labels data/company/train/labels
"""

import argparse
import os
import shutil
from pathlib import Path
import random
from typing import Tuple, List


def organize_images_into_splits(
    image_dir: str,
    output_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42,
):
    """
    Organize images into train/val/test splits.

    Args:
        image_dir: Directory containing all company images
        output_dir: Output directory to create splits
        train_ratio: Proportion for training (default 70%)
        val_ratio: Proportion for validation (default 20%)
        test_ratio: Proportion for testing (default 10%)
        seed: Random seed for reproducibility
    """
    random.seed(seed)
    
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)
    
    # Create output structure
    for split in ["train", "val", "test"]:
        (output_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (output_dir / split / "labels").mkdir(parents=True, exist_ok=True)
    
    # Find all images
    image_extensions = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")
    images = [f for f in image_dir.glob("*") if f.suffix in image_extensions]
    
    print(f"Found {len(images)} images in {image_dir}")
    
    # Shuffle and split
    random.shuffle(images)
    n_train = int(len(images) * train_ratio)
    n_val = int(len(images) * val_ratio)
    
    train_images = images[:n_train]
    val_images = images[n_train : n_train + n_val]
    test_images = images[n_train + n_val :]
    
    # Copy images to splits
    for split, image_list in [
        ("train", train_images),
        ("val", val_images),
        ("test", test_images),
    ]:
        for img in image_list:
            dest = output_dir / split / "images" / img.name
            shutil.copy2(img, dest)
        print(f"  {split}: {len(image_list)} images")
    
    print(f"\n✓ Images organized to {output_dir}")
    print(f"  Expected next step: Annotate labels manually or use label tool")
    print(f"  Then create YOLO format .txt files in each labels/ folder")
    
    return output_dir


def merge_datasets(
    company_dir: str,
    roboflow_dir: str,
    output_dir: str,
    data_yaml_output: str = "data.yaml",
):
    """
    Merge company data with Roboflow data for fine-tuning.

    Args:
        company_dir: Path to organized company dataset
        roboflow_dir: Path to Roboflow raw dataset
        output_dir: Output directory for merged dataset
        data_yaml_output: Output data.yaml filename
    """
    company_dir = Path(company_dir)
    roboflow_dir = Path(roboflow_dir)
    output_dir = Path(output_dir)
    
    # Create output structure
    for split in ["train", "val", "test"]:
        (output_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (output_dir / split / "labels").mkdir(parents=True, exist_ok=True)
    
    # Merge train/val/test
    for split in ["train", "val", "test"]:
        # Copy Roboflow data
        roboflow_images = roboflow_dir / split / "images"
        roboflow_labels = roboflow_dir / split / "labels"
        
        if roboflow_images.exists():
            for img in roboflow_images.glob("*"):
                shutil.copy2(img, output_dir / split / "images" / img.name)
        if roboflow_labels.exists():
            for lbl in roboflow_labels.glob("*.txt"):
                shutil.copy2(lbl, output_dir / split / "labels" / lbl.name)
        
        # Copy company data
        company_images = company_dir / split / "images"
        company_labels = company_dir / split / "labels"
        
        if company_images.exists():
            for img in company_images.glob("*"):
                shutil.copy2(img, output_dir / split / "images" / img.name)
        if company_labels.exists():
            for lbl in company_labels.glob("*.txt"):
                shutil.copy2(lbl, output_dir / split / "labels" / lbl.name)
        
        n_img = len(list((output_dir / split / "images").glob("*")))
        n_lbl = len(list((output_dir / split / "labels").glob("*.txt")))
        print(f"  {split}: {n_img} images, {n_lbl} labels")
    
    print(f"\n✓ Datasets merged to {output_dir}")


def validate_labels(labels_dir: str) -> Tuple[int, int, List[str]]:
    """
    Validate YOLO format labels.

    Args:
        labels_dir: Directory containing .txt label files

    Returns:
        (total_labels, files_with_errors, error_messages)
    """
    labels_dir = Path(labels_dir)
    
    if not labels_dir.exists():
        print(f"❌ Labels directory not found: {labels_dir}")
        return 0, 0, []
    
    label_files = list(labels_dir.glob("*.txt"))
    errors = []
    
    for lbl_file in label_files:
        with open(lbl_file) as f:
            lines = f.readlines()
        
        if not lines:
            errors.append(f"  {lbl_file.name}: Empty file")
            continue
        
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) != 5:
                errors.append(
                    f"  {lbl_file.name}:{i+1}: Expected 5 values, got {len(parts)}"
                )
                continue
            
            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Validate ranges
                if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and
                        0 < width <= 1 and 0 < height <= 1):
                    errors.append(
                        f"  {lbl_file.name}:{i+1}: Coordinates out of range [0-1]"
                    )
            except ValueError as e:
                errors.append(f"  {lbl_file.name}:{i+1}: Invalid format: {e}")
    
    print(f"\nValidation Summary:")
    print(f"  Total label files: {len(label_files)}")
    print(f"  Files with errors: {len(set(e.split(':')[0] for e in errors))}")
    
    if errors:
        print(f"\n⚠ Errors found:")
        for err in errors[:10]:  # Show first 10 errors
            print(err)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    else:
        print(f"  ✓ All labels are valid!")
    
    return len(label_files), len(errors), errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare company data for YOLOv11 fine-tuning"
    )
    parser.add_argument("--company-dir", type=str, help="Directory with company car images")
    parser.add_argument("--roboflow-dir", type=str, help="Directory with Roboflow dataset")
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument(
        "--merge", action="store_true", help="Merge company + Roboflow datasets"
    )
    parser.add_argument(
        "--validate-labels", type=str, help="Validate labels in directory"
    )
    parser.add_argument("--train-ratio", type=float, default=0.7, help="Train split ratio")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Val split ratio")
    parser.add_argument("--test-ratio", type=float, default=0.1, help="Test split ratio")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("  YOLOv11 Company Data Preparation Tool")
    print("=" * 70)
    
    if args.validate_labels:
        validate_labels(args.validate_labels)
    
    elif args.merge and args.company_dir and args.roboflow_dir and args.output:
        print(f"\nMerging datasets...")
        merge_datasets(args.company_dir, args.roboflow_dir, args.output)
    
    elif args.company_dir and args.output:
        print(f"\nOrganizing company images into train/val/test splits...")
        organize_images_into_splits(
            args.company_dir,
            args.output,
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            test_ratio=args.test_ratio,
        )
    
    else:
        parser.print_help()
    
    print("=" * 70 + "\n")
