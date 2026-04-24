"""
inspect_pickles.py - View the structure of all pickle files
"""
import pickle
import numpy as np

# =============================================
# 1. data.pickle (raw dataset)
# =============================================
print("=" * 65)
print("1. data.pickle (raw dataset from create_dataset.py)")
print("=" * 65)
d = pickle.load(open("data.pickle", "rb"))
print(f"  Keys: {list(d.keys())}")
data_list = d["data"]
labels_list = d["labels"]
print(f"  data  : {len(data_list)} samples, each has {len(data_list[0])} features")
print(f"  labels: {len(labels_list)} labels")
print(f"  Sample data[0] (first 6 values): {data_list[0][:6]}")
print(f"  Sample label[0]: {labels_list[0]} (= letter {chr(int(labels_list[0])+65)})")

# =============================================
# 2. split_data.pickle (group-based split)
# =============================================
print()
print("=" * 65)
print("2. split_data.pickle (from split_data.py)")
print("=" * 65)
s = pickle.load(open("split_data.pickle", "rb"))
print(f"  Keys: {list(s.keys())}")
print(f"  x_train : shape {s['x_train'].shape}")
print(f"  y_train : shape {s['y_train'].shape}")
print(f"  x_val   : shape {s['x_val'].shape}")
print(f"  x_test  : shape {s['x_test'].shape}")
print(f"  groups  : {len(s['groups'])} entries, {len(np.unique(s['groups']))} unique groups")
print(f"  config  : {s['config']}")

# =============================================
# 3. augmented_split.pickle (augmented)
# =============================================
print()
print("=" * 65)
print("3. augmented_split.pickle (from augment_data.py)")
print("=" * 65)
a = pickle.load(open("augmented_split.pickle", "rb"))
print(f"  Keys: {list(a.keys())}")
print(f"  x_train : shape {a['x_train'].shape}  (augmented!)")
print(f"  y_train : shape {a['y_train'].shape}")
print(f"  x_val   : shape {a['x_val'].shape}   (NOT augmented)")
print(f"  x_test  : shape {a['x_test'].shape}  (NOT augmented)")
print(f"  config  : {a['config']}")

# =============================================
# 4. What ONE data point looks like
# =============================================
print()
print("=" * 65)
print("4. SAMPLE: What one data point looks like")
print("=" * 65)
sample = a["x_train"][0]
label = a["y_train"][0]
print(f"  Letter: {chr(int(label)+65)} (label={label})")
print(f"  Features: 42 values = 21 landmarks x 2 coords (x, y)")
print()
for i in range(21):
    x = sample[i * 2]
    y = sample[i * 2 + 1]
    print(f"    Landmark {i:2d}: x={x:.6f}, y={y:.6f}")
