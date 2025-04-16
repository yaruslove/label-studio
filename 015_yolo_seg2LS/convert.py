#!/usr/bin/env python3
import os
import json
import yaml
import argparse
import cv2
import numpy as np
import hashlib
import secrets
import copy


def parse_args():
    parser = argparse.ArgumentParser(description='Convert YOLO segmentation format to Label Studio JSON')
    parser.add_argument('--config', type=str, required=True, help='Path to the YAML config file')
    return parser.parse_args()


def read_classes(classes_file):
    """Read class names from file"""
    with open(classes_file, 'r') as f:
        return [line.strip() for line in f.readlines()]


def read_yolo_segmentation(label_file):
    """Read YOLO segmentation format from txt file"""
    segments = []
    with open(label_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:  # At least class_id + 2 points (4 coordinates)
                continue
            
            class_id = int(parts[0])
            
            # Parse polygon points (x1 y1 x2 y2 ...)
            points = []
            for i in range(1, len(parts), 2):
                if i+1 < len(parts):
                    x = float(parts[i]) * 100  # Convert to percentage
                    y = float(parts[i+1]) * 100  # Convert to percentage
                    points.append([x, y])
            
            if len(points) >= 3:  # Need at least 3 points for a polygon
                segments.append({
                    "class_id": class_id,
                    "points": points
                })
    
    return segments


def get_image_resolution(image_path):
    """Get image width and height"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    height, width = img.shape[:2]
    return width, height


def generate_unique_id(length=10):
    """Generate a random unique ID for Label Studio annotations"""
    return ''.join(secrets.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(length))


def generate_uuid():
    """Generate a UUID format string for annotations"""
    hash1 = hashlib.sha1(secrets.token_urlsafe(8).encode("UTF-8")).hexdigest()[:8]
    hash2 = hashlib.sha1(secrets.token_urlsafe(4).encode("UTF-8")).hexdigest()[:4]
    hash3 = hashlib.sha1(secrets.token_urlsafe(4).encode("UTF-8")).hexdigest()[:4]
    hash4 = hashlib.sha1(secrets.token_urlsafe(12).encode("UTF-8")).hexdigest()[:12]
    return f"{hash1}-{hash2}-{hash3}-{hash4}"


def create_task_annotation(image_path, label_file, class_names, task_id):
    """Create a Label Studio task annotation from YOLO segmentation data"""
    # Get image dimensions
    width, height = get_image_resolution(image_path)
    
    # Read segmentation data
    segments = read_yolo_segmentation(label_file)
    
    # Create annotation structure
    annotation = {
        "id": task_id,
        "completed_by": 1,  # Default user ID
        "result": [],
        "was_cancelled": False,
        "ground_truth": False,
        "created_at": "2025-04-16T10:00:00.000000Z",  # Use current date
        "updated_at": "2025-04-16T10:00:00.000000Z",  # Use current date
        "lead_time": 0,
        "prediction": {},
        "result_count": 0,
        "unique_id": generate_uuid(),
        "task": task_id,
        "project": 1  # Default project ID
    }
    
    # Add segmentation results
    for segment in segments:
        class_id = segment["class_id"]
        
        # Skip if class ID is out of range
        if class_id >= len(class_names):
            continue
        
        # Create result for this segment
        result = {
            "original_width": width,
            "original_height": height,
            "image_rotation": 0,
            "value": {
                "points": segment["points"],
                "closed": True,
                "polygonlabels": [class_names[class_id]]
            },
            "id": generate_unique_id(),
            "from_name": "label",  # Standard name in Label Studio
            "to_name": "image",    # Standard name in Label Studio
            "type": "polygonlabels",
            "origin": "manual"
        }
        
        annotation["result"].append(result)
    
    return annotation


def main():
    # Parse command line arguments
    config ="config.yaml"
    
    # Load config
    with open(config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract parameters from config
    labels_path = config.get('labels_path')
    images_path = config.get('images_path')
    path_prefix = config.get('path_prefix')
    classes_file = config.get('classes')
    ls_json_file = config.get('LS_json')
    
    # Validate parameters
    if not all([labels_path, images_path, path_prefix, classes_file, ls_json_file]):
        missing = []
        if not labels_path: missing.append('labels_path')
        if not images_path: missing.append('images_path')
        if not path_prefix: missing.append('path_prefix')
        if not classes_file: missing.append('classes_file')
        if not ls_json_file: missing.append('ls_json_file')
        raise ValueError(f"Missing required parameters in config: {', '.join(missing)}")
    
    # Load class names
    class_names = read_classes(classes_file)
    
    # Fixed prefix for Label Studio images (always static)
    static_prefix = "/data/local-files/?d="
    
    # Get all label files
    label_files = [f for f in os.listdir(labels_path) if f.endswith('.txt')]
    
    # Create Label Studio tasks
    tasks = []
    for task_id, label_file in enumerate(label_files, start=1):
        label_path = os.path.join(labels_path, label_file)
        
        # Get base name without extension
        base_name = os.path.splitext(label_file)[0]
        
        # Find corresponding image (try different extensions)
        image_file = None
        for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
            img_name = base_name + ext
            img_path = os.path.join(images_path, img_name)
            if os.path.exists(img_path):
                image_file = img_name
                break
        
        if not image_file:
            print(f"Warning: No image found for label {label_file}")
            continue
        
        # Construct Label Studio image path
        image_path = os.path.join(images_path, image_file)
        ls_image_path = f"{static_prefix}{path_prefix}{image_file}"
        
        # Create annotation
        annotation = create_task_annotation(image_path, label_path, class_names, task_id)
        
        # Create task structure
        task = {
            "id": task_id,
            "annotations": [annotation],
            "predictions": [],
            "data": {
                "image": ls_image_path
            },
            "meta": {},
            "created_at": "2025-04-16T10:00:00.000000Z",  # Use current date
            "updated_at": "2025-04-16T10:00:00.000000Z",  # Use current date
            "inner_id": task_id,
            "total_annotations": 1,
            "project": 1  # Default project ID
        }
        
        tasks.append(task)
    
    # Save Label Studio JSON
    with open(ls_json_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    print(f"Conversion complete! {len(tasks)} tasks saved to {ls_json_file}")


if __name__ == "__main__":
    main()