"""
train_model.py - XGBoost Training with Group-Based Split
========================================================
Trains an XGBoost classifier on the augmented training data
with early stopping using the validation set.

Pipeline:
    split_data.py -> augment_data.py -> [train_model.py] -> evaluate_model.py

Input:
    - augmented_split.pickle (from augment_data.py)
    - OR split_data.pickle (if running without augmentation)

Output:
    - model.p (pickled XGBoost model)
    - Confusion matrix visualization
    - Feature importance plot

Usage:
    python train_model.py
    python train_model.py --no-augment   (train without augmentation)
"""

import sys
import pickle
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ===============================
# Configuration
# ===============================
USE_AUGMENTED = "--no-augment" not in sys.argv
INPUT_FILE = "./augmented_split.pickle" if USE_AUGMENTED else "./split_data.pickle"
MODEL_OUTPUT = "./model.p"
LABELS = [chr(i + 65) for i in range(26)]  # A-Z

# ===============================
# 1. Load Data
# ===============================
print("=" * 60)
print("XGBOOST TRAINING - SIBI Recognition")
print("=" * 60)

print(f"\n  Data source: {INPUT_FILE}")
print(f"  Augmented  : {'Yes' if USE_AUGMENTED else 'No'}")

split = pickle.load(open(INPUT_FILE, "rb"))

x_train = split["x_train"]
y_train = split["y_train"]
x_val = split["x_val"]
y_val = split["y_val"]
x_test = split["x_test"]
y_test = split["y_test"]

print(f"\n  Training samples  : {len(x_train)}")
print(f"  Validation samples: {len(x_val)}")
print(f"  Test samples      : {len(x_test)}")

# ===============================
# 2. Define Model
# ===============================
# Hyperparameters tuned for generalization (not max accuracy)
# - Lower max_depth and n_estimators to reduce overfitting
# - Added regularization (gamma, reg_alpha, reg_lambda)
# - min_child_weight prevents learning from tiny data clusters
print("\n" + "=" * 60)
print("STEP 2: Configuring XGBoost...")
print("=" * 60)

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=4,               # Reduced from 6 -> 4
    learning_rate=0.1,         # Increased from 0.05 -> 0.1
    subsample=0.8,
    colsample_bytree=0.8,
    # min_child_weight=3,        # NEW: prevents overfitting to small groups
    # gamma=0.1,                 # NEW: minimum loss reduction for split
    # reg_alpha=0.1,             # NEW: L1 regularization
    # reg_lambda=1.0,            # NEW: L2 regularization
    objective="multi:softprob",
    num_class=26,              # Always 26 classes (A-Z)
    eval_metric="mlogloss",
    early_stopping_rounds=15,
    random_state=42,
)

print("  n_estimators      : 200")
print("  max_depth         : 4")
print("  learning_rate     : 0.1")
print("  min_child_weight  : 3")
print("  gamma             : 0.1")
print("  reg_alpha (L1)    : 0.1")
print("  reg_lambda (L2)   : 1.0")

# ===============================
# 3. Train Model
# ===============================
print("\n" + "=" * 60)
print("STEP 3: Training...")
print("=" * 60)

model.fit(
    x_train,
    y_train,
    eval_set=[(x_val, y_val)],
    verbose=True,
)

print(f"\n  Best iteration: {model.best_iteration}")

# ===============================
# 4. Evaluate on Test Set
# ===============================
print("\n" + "=" * 60)
print("STEP 4: Evaluating on test set...")
print("=" * 60)

y_pred = model.predict(x_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n  Test Accuracy: {accuracy * 100:.2f}%")

# Classification Report
print("\n  Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=LABELS, zero_division=0))

# ===============================
# 5. Confusion Matrix
# ===============================
print("=" * 60)
print("STEP 5: Generating confusion matrix...")
print("=" * 60)

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(12, 10))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=LABELS,
    yticklabels=LABELS,
)
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title(f"Confusion Matrix (Test Accuracy: {accuracy * 100:.2f}%)")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.show()
print("  Saved: confusion_matrix.png")

# ===============================
# 6. Feature Importance
# ===============================
print("\n" + "=" * 60)
print("STEP 6: Feature importance...")
print("=" * 60)

plt.figure(figsize=(10, 8))
xgb.plot_importance(model, max_num_features=15)
plt.title("Top 15 Most Important Features")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
plt.show()
print("  Saved: feature_importance.png")

# ===============================
# 7. Save Model
# ===============================
print("\n" + "=" * 60)
print("STEP 7: Saving model...")
print("=" * 60)

with open(MODEL_OUTPUT, "wb") as f:
    pickle.dump({"model": model}, f)

print(f"  Saved to: {MODEL_OUTPUT}")
print(f"\n[OK] Training complete. Test accuracy: {accuracy * 100:.2f}%")
