import pickle
import numpy as np

d = pickle.load(open("data.pickle", "rb"))
labels = [int(l) for l in d["labels"]]

print("Samples per class:")
print("-" * 30)
for c in range(26):
    count = labels.count(c)
    letter = chr(c + 65)
    print(f"  {letter} (class {c:2d}): {count} samples")
print(f"\nTotal: {len(labels)} samples")
print(f"Min: {min(labels.count(c) for c in range(26))}")
print(f"Max: {max(labels.count(c) for c in range(26))}")
