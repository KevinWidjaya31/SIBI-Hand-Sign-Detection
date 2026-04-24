"""
augment_data.py - Landmark-Based Data Augmentation (Train Only)
===============================================================
Applies geometric and noise augmentations to hand landmark data
to increase training set diversity and improve model generalization.

Transformations applied:
  1. Rotation     : +10 degrees around centroid
  2. Scaling      : 0.9x - 1.1x uniform scaling
  3. Translation  : +0.05 shift in x and y
  4. Gaussian Noise: - = 0.01

Important:
  - Augmentation is applied ONLY to training data
  - Validation and test sets remain unmodified
  - This script reads from split_data.pickle (produced by split_data.py)

Output:
  - saves augmented_split.pickle with augmented training data

Usage:
    python augment_data.py
"""

import pickle
import numpy as np

# ===============================
# Configuration
# ===============================
INPUT_FILE = "./split_data.pickle"
OUTPUT_FILE = "./augmented_split.pickle"
AUGMENT_COPIES = 2     # Number of augmented copies per original sample


# ===============================
# Augmentation Functions
# ===============================
def augment_landmarks(landmarks, config=None):
    """
    Apply random geometric and noise augmentations to a single
    set of hand landmarks (42-element array: 21 points x 2 coords).

    Parameters:
        landmarks : np.ndarray of shape (42,)
        config    : dict with optional overrides for augmentation params

    Returns:
        np.ndarray of shape (42,) - augmented landmarks
    """
    if config is None:
        config = {}

    # Default augmentation parameters
    rotation_range = config.get("rotation_range", 10)      # degrees
    scale_range = config.get("scale_range", (0.9, 1.1))
    shift_range = config.get("shift_range", 0.05)
    noise_std = config.get("noise_std", 0.01)

    # Reshape to (21, 2) for geometric operations
    lm = np.array(landmarks).reshape(-1, 2)

    # --- 1. Rotation around centroid ---
    centroid = lm.mean(axis=0)
    lm_centered = lm - centroid

    angle = np.random.uniform(-rotation_range, rotation_range)
    theta = np.radians(angle)
    rotation_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    lm_centered = np.dot(lm_centered, rotation_matrix)
    lm = lm_centered + centroid

    # --- 2. Uniform Scaling ---
    scale = np.random.uniform(scale_range[0], scale_range[1])
    lm = centroid + (lm - centroid) * scale

    # --- 3. Translation ---
    shift = np.random.uniform(-shift_range, shift_range, size=(1, 2))
    lm = lm + shift

    # --- 4. Gaussian Noise ---
    noise = np.random.normal(0, noise_std, lm.shape)
    lm = lm + noise

    return lm.flatten()


def augment_dataset(x_data, y_labels, n_copies=2, config=None):
    """
    Augment an entire dataset by creating n_copies augmented
    versions of each sample.

    Parameters:
        x_data   : np.ndarray of shape (N, 42)
        y_labels : np.ndarray of shape (N,)
        n_copies : int, number of augmented copies per sample
        config   : dict, augmentation parameters

    Returns:
        Tuple of (augmented_x, augmented_y) including originals
    """
    augmented_x = list(x_data)       # Start with original samples
    augmented_y = list(y_labels)

    for x, y in zip(x_data, y_labels):
        for _ in range(n_copies):
            aug_x = augment_landmarks(x, config)
            augmented_x.append(aug_x)
            augmented_y.append(y)

    return np.array(augmented_x), np.array(augmented_y)


# ===============================
# Main Execution
# ===============================
if __name__ == "__main__":
    print("=" * 60)
    print("LANDMARK DATA AUGMENTATION (Train Only)")
    print("=" * 60)

    # --- Load split data ---
    print("\nLoading split data...")
    split = pickle.load(open(INPUT_FILE, "rb"))

    x_train = split["x_train"]
    y_train = split["y_train"]
    x_val = split["x_val"]
    y_val = split["y_val"]
    x_test = split["x_test"]
    y_test = split["y_test"]

    print(f"  Original training set   : {len(x_train)} samples")
    print(f"  Validation set (no aug) : {len(x_val)} samples")
    print(f"  Test set (no aug)       : {len(x_test)} samples")

    # --- Augment ONLY training data ---
    print(f"\nAugmenting training data ({AUGMENT_COPIES} copies per sample)...")

    x_train_aug, y_train_aug = augment_dataset(
        x_train, y_train,
        n_copies=AUGMENT_COPIES,
        config={
            "rotation_range": 10,
            "scale_range": (0.9, 1.1),
            "shift_range": 0.05,
            "noise_std": 0.01,
        }
    )

    print(f"  Augmented training set  : {len(x_train_aug)} samples "
          f"({len(x_train)} original + {len(x_train_aug) - len(x_train)} augmented)")

    # --- Verify class balance ---
    print("\n  Class distribution (augmented training):")
    unique, counts = np.unique(y_train_aug, return_counts=True)
    for cls, cnt in zip(unique, counts):
        print(f"    {chr(int(cls) + 65)}: {cnt}")

    # --- Save augmented split ---
    print(f"\nSaving to {OUTPUT_FILE}...")

    output = {
        "x_train": x_train_aug,
        "y_train": y_train_aug,
        "x_val": x_val,            # NOT augmented
        "y_val": y_val,
        "x_test": x_test,          # NOT augmented
        "y_test": y_test,
        "config": {
            "augment_copies": AUGMENT_COPIES,
            "original_train_size": len(x_train),
            "augmented_train_size": len(x_train_aug),
        }
    }

    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump(output, f)

    print("\n[OK] Augmentation complete.")
    print(f"   Training: {len(x_train)} -> {len(x_train_aug)} samples")
    print(f"   Val/Test: Unchanged (no augmentation applied)")
