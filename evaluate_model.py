"""
evaluate_model.py - Comprehensive Model Evaluation + Noise Robustness
=====================================================================
Evaluates the trained XGBoost model with:
  1. Standard metrics (Accuracy, Precision, Recall, F1, mAP)
  2. Per-letter accuracy breakdown
  3. Confusion matrix visualization
  4. Noise robustness testing at multiple - levels
  5. Summary comparison table

Pipeline:
    split_data.py -> augment_data.py -> train_model.py -> [evaluate_model.py]

Input:
    - model.p (from train_model.py)
    - augmented_split.pickle or split_data.pickle (for test data)

Usage:
    python evaluate_model.py
"""

import pickle
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import label_binarize
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)

# ===============================
# Configuration
# ===============================
MODEL_FILE = "./model.p"
SPLIT_FILE = "./augmented_split.pickle"  # Uses the same split as training
LABELS = [chr(i + 65) for i in range(26)]  # A-Z
NOISE_LEVELS = [0.0, 0.01, 0.02, 0.05, 0.1]  # - values for robustness testing


# ===============================
# Evaluation Functions
# ===============================
def compute_metrics(model, x_test, y_test, class_labels):
    """
    Compute all classification metrics.

    Returns:
        dict with accuracy, precision, recall, f1, mAP, confusion_matrix,
        classification_report, and per-letter accuracy.
    """
    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)

    # Core metrics (macro averaged)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

    # mAP (One-vs-Rest)
    unique_classes = np.unique(np.concatenate([y_test, y_pred]))
    y_test_bin = label_binarize(y_test, classes=class_labels)
    try:
        map_score = average_precision_score(y_test_bin, y_proba, average="macro")
    except ValueError:
        map_score = 0.0

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=class_labels)

    # Per-letter accuracy
    per_letter = []
    for i, cls in enumerate(class_labels):
        mask = y_test == cls
        if mask.sum() > 0:
            letter_acc = accuracy_score(y_test[mask], y_pred[mask])
        else:
            letter_acc = 0.0
        per_letter.append({
            "letter": chr(int(cls) + 65),
            "accuracy": letter_acc,
            "support": int(mask.sum()),
        })

    # Classification report
    report = classification_report(
        y_test, y_pred,
        target_names=[chr(int(c) + 65) for c in class_labels],
        output_dict=True,
        zero_division=0,
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "mAP": map_score,
        "confusion_matrix": cm,
        "classification_report": report,
        "per_letter": per_letter,
        "y_pred": y_pred,
    }


def noise_robustness_test(model, x_test, y_test, noise_levels):
    """
    Test model accuracy under varying levels of Gaussian noise.

    Parameters:
        model        : trained classifier
        x_test       : test features
        y_test       : test labels
        noise_levels : list of - values

    Returns:
        list of dicts with {sigma, accuracy, precision, recall, f1}
    """
    results = []
    for sigma in noise_levels:
        if sigma == 0:
            x_noisy = x_test.copy()
        else:
            noise = np.random.normal(0, sigma, x_test.shape)
            x_noisy = x_test + noise

        y_pred = model.predict(x_noisy)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
        rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1_val = f1_score(y_test, y_pred, average="macro", zero_division=0)

        results.append({
            "sigma": sigma,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1_val,
        })

    return results


# ===============================
# Main Execution
# ===============================
if __name__ == "__main__":
    print("=" * 70)
    print("MODEL EVALUATION - SIBI Recognition (XGBoost + MediaPipe)")
    print("=" * 70)

    # --- Load model ---
    print("\nLoading model...")
    model_dict = pickle.load(open(MODEL_FILE, "rb"))
    model = model_dict["model"]

    # --- Load test data ---
    print("Loading test data...")
    split = pickle.load(open(SPLIT_FILE, "rb"))
    x_test = split["x_test"]
    y_test = split["y_test"]
    class_labels = np.unique(y_test)

    print(f"  Model      : {MODEL_FILE}")
    print(f"  Test samples: {len(x_test)}")

    # ═══════════════════════════════════
    # 1. STANDARD METRICS
    # ═══════════════════════════════════
    print("\n" + "=" * 70)
    print("1. STANDARD METRICS")
    print("=" * 70)

    metrics = compute_metrics(model, x_test, y_test, class_labels)

    print(f"\n  Accuracy  : {metrics['accuracy'] * 100:.2f}%")
    print(f"  Precision : {metrics['precision'] * 100:.2f}%")
    print(f"  Recall    : {metrics['recall'] * 100:.2f}%")
    print(f"  F1-Score  : {metrics['f1_score'] * 100:.2f}%")
    print(f"  mAP       : {metrics['mAP'] * 100:.2f}%")

    # ═══════════════════════════════════
    # 2. PER-LETTER ACCURACY
    # ═══════════════════════════════════
    print("\n" + "=" * 70)
    print("2. PER-LETTER ACCURACY")
    print("=" * 70)

    print(f"\n  {'Letter':<8} {'Accuracy':>10} {'Support':>10}")
    print("  " + "-" * 30)
    for pl in metrics["per_letter"]:
        acc_str = f"{pl['accuracy'] * 100:.1f}%"
        print(f"  {pl['letter']:<8} {acc_str:>10} {pl['support']:>10}")

    # ═══════════════════════════════════
    # 3. CLASSIFICATION REPORT
    # ═══════════════════════════════════
    print("\n" + "=" * 70)
    print("3. CLASSIFICATION REPORT")
    print("=" * 70)
    print()

    report = classification_report(
        y_test, metrics["y_pred"],
        target_names=[chr(int(c) + 65) for c in class_labels],
        zero_division=0,
    )
    print(report)

    # ═══════════════════════════════════
    # 4. CONFUSION MATRIX
    # ═══════════════════════════════════
    print("=" * 70)
    print("4. CONFUSION MATRIX")
    print("=" * 70)

    cm = metrics["confusion_matrix"]
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
    plt.title(f"Confusion Matrix (Accuracy: {metrics['accuracy'] * 100:.2f}%)")
    plt.tight_layout()
    plt.savefig("eval_confusion_matrix.png", dpi=150)
    plt.show()
    print("  Saved: eval_confusion_matrix.png")

    # ═══════════════════════════════════
    # 5. NOISE ROBUSTNESS TEST
    # ═══════════════════════════════════
    print("\n" + "=" * 70)
    print("5. NOISE ROBUSTNESS TEST")
    print("=" * 70)

    np.random.seed(42)  # Reproducibility
    noise_results = noise_robustness_test(model, x_test, y_test, NOISE_LEVELS)

    print(f"\n  {'Noise -':<10} {'Accuracy':>10} {'Precision':>12} "
          f"{'Recall':>10} {'F1-Score':>10}")
    print("  " + "-" * 56)

    for r in noise_results:
        sigma_str = f"-={r['sigma']:.2f}" if r["sigma"] > 0 else "Clean"
        print(f"  {sigma_str:<10} {r['accuracy']*100:>9.2f}% "
              f"{r['precision']*100:>11.2f}% {r['recall']*100:>9.2f}% "
              f"{r['f1']*100:>9.2f}%")

    # Plot robustness curve
    sigmas = [r["sigma"] for r in noise_results]
    accs = [r["accuracy"] * 100 for r in noise_results]

    plt.figure(figsize=(8, 5))
    plt.plot(sigmas, accs, "o-", color="black", linewidth=2, markersize=8)
    plt.xlabel("Noise - (Gaussian)")
    plt.ylabel("Accuracy (%)")
    plt.title("Model Robustness Under Noise Perturbation")
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig("noise_robustness.png", dpi=150)
    plt.show()
    print("\n  Saved: noise_robustness.png")

    # ═══════════════════════════════════
    # 6. SUMMARY
    # ═══════════════════════════════════
    print("\n" + "=" * 70)
    print("6. EVALUATION SUMMARY")
    print("=" * 70)

    print(f"""
  +----------------------------------------+
  | Accuracy  : {metrics['accuracy'] * 100:>6.2f}%                  |
  | Precision : {metrics['precision'] * 100:>6.2f}%                  |
  | Recall    : {metrics['recall'] * 100:>6.2f}%                  |
  | F1-Score  : {metrics['f1_score'] * 100:>6.2f}%                  |
  | mAP       : {metrics['mAP'] * 100:>6.2f}%                  |
  +----------------------------------------+
  | Test samples: {len(x_test):<25}|
  | Noise s=0.05 acc: {noise_results[3]['accuracy']*100:>5.2f}%             |
  | Noise s=0.10 acc: {noise_results[4]['accuracy']*100:>5.2f}%             |
  +----------------------------------------+
    """)

    print("[OK] Evaluation complete.")
