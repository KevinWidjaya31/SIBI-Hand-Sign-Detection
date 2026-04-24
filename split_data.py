"""
split_data.py -- Group-Based Data Splitting for SIBI Recognition
================================================================
Splits the dataset ensuring that consecutive frames from the same
recording burst NEVER appear in both training and test sets.

Context:
- Dataset was collected via collect_imgs.py in sessions of ~100 frames.
- Some images fail MediaPipe detection, so actual counts vary (61-200).
- We use BURST_SIZE=50 to ensure every class gets 2+ groups.

Strategy:
- Divide each class's samples into groups of BURST_SIZE consecutive frames
- For each class: assign 1 group to test, rest to train
- Then hold out a portion of training as validation

Output:
- saves split_data.pickle containing train/val/test splits with group info

Usage:
    python split_data.py
"""

import pickle
import numpy as np

# ===============================
# Configuration
# ===============================
INPUT_FILE = "./data.pickle"
OUTPUT_FILE = "./split_data.pickle"
BURST_SIZE = 50         # Smaller burst = more groups per class (important!)
VAL_RATIO = 0.2         # Fraction of training data to use as validation

# ===============================
# 1. Load Dataset
# ===============================
print("=" * 60)
print("STEP 1: Loading dataset...")
print("=" * 60)

data_dict = pickle.load(open(INPUT_FILE, "rb"))
data = np.asarray(data_dict["data"])
labels = np.asarray([int(label) for label in data_dict["labels"]])

print(f"  Total samples : {len(data)}")
print(f"  Feature shape : {data.shape}")
print(f"  Unique classes: {len(np.unique(labels))}")

# ===============================
# 2. Generate Group IDs
# ===============================
# Each class's samples are in temporal order from collection.
# We split them into bursts of BURST_SIZE frames.
# Each burst gets a UNIQUE group ID.
#
# With BURST_SIZE=50:
#   Class with 100 samples -> 2 groups
#   Class with 200 samples -> 4 groups
#   Class with 61 samples  -> 2 groups (50 + 11)
print("\n" + "=" * 60)
print("STEP 2: Assigning group IDs based on recording bursts...")
print("=" * 60)

groups = np.zeros(len(data), dtype=int)
group_counter = 0
class_groups = {}  # class_id -> list of group_ids

for class_id in sorted(np.unique(labels)):
    class_mask = labels == class_id
    class_indices = np.where(class_mask)[0]
    n_samples = len(class_indices)

    # Always create at least 2 groups per class
    n_bursts = max(2, n_samples // BURST_SIZE)

    class_groups[class_id] = []

    # Calculate samples per burst (evenly distributed)
    base_size = n_samples // n_bursts
    remainder = n_samples % n_bursts

    offset = 0
    for burst_idx in range(n_bursts):
        # Distribute remainder evenly across first bursts
        burst_size = base_size + (1 if burst_idx < remainder else 0)
        burst_indices = class_indices[offset:offset + burst_size]
        groups[burst_indices] = group_counter
        class_groups[class_id].append(group_counter)
        group_counter += 1
        offset += burst_size

print(f"  Total groups created: {group_counter}")
print(f"  Groups per class   : ~{group_counter // len(np.unique(labels))}")

# Show per-class group info
for class_id in sorted(np.unique(labels)):
    class_mask = labels == class_id
    n = int(class_mask.sum())
    n_g = len(class_groups[class_id])
    letter = chr(class_id + 65)
    sizes = []
    for g in class_groups[class_id]:
        sizes.append(int((groups == g).sum()))
    print(f"  {letter}: {n} samples -> {n_g} groups (sizes: {sizes})")

unique_groups, group_counts = np.unique(groups, return_counts=True)
print(f"\n  Group size range: {group_counts.min()} - {group_counts.max()} samples")

# ===============================
# 3. Split by Group (per class)
# ===============================
# For each class, assign one group to test and rest to train.
# This guarantees:
#   - Every class appears in both train and test
#   - No group leakage (entire bursts stay together)
#   - Clean separation of recording sessions
print("\n" + "=" * 60)
print("STEP 3: Splitting by group (per class)...")
print("=" * 60)

np.random.seed(42)

train_indices = []
test_indices = []

for class_id in sorted(np.unique(labels)):
    g_list = class_groups[class_id]

    # Randomly select 1 group for test, rest for train
    test_group = np.random.choice(g_list)
    train_group_list = [g for g in g_list if g != test_group]

    # Get indices for test
    test_mask = (groups == test_group) & (labels == class_id)
    test_indices.extend(np.where(test_mask)[0])

    # Get indices for train
    for g in train_group_list:
        train_mask = (groups == g) & (labels == class_id)
        train_indices.extend(np.where(train_mask)[0])

    letter = chr(class_id + 65)
    n_test = int(test_mask.sum())
    n_train = sum(int(((groups == g) & (labels == class_id)).sum()) for g in train_group_list)
    print(f"  {letter}: {len(g_list)} groups -> train={len(train_group_list)} ({n_train}) "
          f"test=1 ({n_test})")

train_indices = np.array(train_indices)
test_indices = np.array(test_indices)

# ===============================
# 4. Hold out validation from training
# ===============================
print("\n" + "=" * 60)
print("STEP 4: Holding out validation set from training...")
print("=" * 60)

np.random.shuffle(train_indices)
n_val = int(len(train_indices) * VAL_RATIO)
val_indices = train_indices[:n_val]
train_indices = train_indices[n_val:]

x_train, y_train = data[train_indices], labels[train_indices]
x_val, y_val = data[val_indices], labels[val_indices]
x_test, y_test = data[test_indices], labels[test_indices]

print(f"  Training set  : {len(x_train)} samples")
print(f"  Validation set: {len(x_val)} samples")
print(f"  Test set      : {len(x_test)} samples")
print(f"  Total         : {len(x_train) + len(x_val) + len(x_test)} "
      f"(original: {len(data)})")

# Verify class coverage
train_classes = set(np.unique(y_train))
val_classes = set(np.unique(y_val))
test_classes = set(np.unique(y_test))
print(f"\n  Classes in train: {len(train_classes)}/26")
print(f"  Classes in val  : {len(val_classes)}/26")
print(f"  Classes in test : {len(test_classes)}/26")

# Verify no group leakage between train+val and test
train_val_groups = set(groups[np.concatenate([train_indices, val_indices])])
test_groups_set = set(groups[test_indices])
overlap = train_val_groups & test_groups_set
print(f"\n  Group overlap (train+val & test): {len(overlap)} <-- must be 0")

if len(overlap) > 0:
    print("  [WARNING] Data leakage detected! Check group assignment.")
else:
    print("  [OK] No data leakage detected.")

# ===============================
# 5. Save Split
# ===============================
print("\n" + "=" * 60)
print("STEP 5: Saving split data...")
print("=" * 60)

split_output = {
    "x_train": x_train,
    "y_train": y_train,
    "x_val": x_val,
    "y_val": y_val,
    "x_test": x_test,
    "y_test": y_test,
    "groups": groups,
    "train_idx": train_indices,
    "val_idx": val_indices,
    "test_idx": test_indices,
    "config": {
        "burst_size": BURST_SIZE,
        "val_ratio": VAL_RATIO,
        "total_groups": group_counter,
    }
}

with open(OUTPUT_FILE, "wb") as f:
    pickle.dump(split_output, f)

print(f"  Saved to: {OUTPUT_FILE}")
print("\n[OK] Group-based split complete. No data leakage.")
