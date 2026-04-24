from flask import Flask, request, jsonify
import numpy as np
import pickle
import json
import os
from datetime import datetime
from flask_cors import CORS
from sklearn.preprocessing import label_binarize
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

# Load XGBoost model
model = pickle.load(open("model.p", "rb"))["model"]

# Load split data for evaluation (uses group-based split, no leakage)
# Try augmented_split first, fall back to split_data, then raw data.pickle
SPLIT_FILE = None
for candidate in ["augmented_split.pickle", "split_data.pickle"]:
    if os.path.exists(candidate):
        SPLIT_FILE = candidate
        break

if SPLIT_FILE:
    _split = pickle.load(open(SPLIT_FILE, "rb"))
    eval_x_test = _split["x_test"]
    eval_y_test = _split["y_test"]
    print(f"[app.py] Loaded evaluation split from {SPLIT_FILE} ({len(eval_x_test)} test samples)")
else:
    # Fallback: load raw data (not recommended — will use random split)
    _data_dict = pickle.load(open("data.pickle", "rb"))
    eval_x_test = np.asarray(_data_dict["data"])
    eval_y_test = np.asarray([int(l) for l in _data_dict["labels"]])
    print(f"[app.py] WARNING: No split file found. Using full data.pickle for eval.")

LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOGS_DIR = "./logs"
os.makedirs(LOGS_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json.get("landmarks", None)

    if data is None or len(data) != 42:  # 21 titik * (x,y)
        return jsonify({"error": "Invalid landmark data"}), 400

    # Convert to numpy
    X = np.asarray([data])

    # Perform prediction
    probabilities = model.predict_proba(X)[0]
    idx = int(np.argmax(probabilities))
    confidence = float(probabilities[idx] * 100)

    # Top-3 predictions
    top3_idx = np.argsort(probabilities)[::-1][:3]
    top3 = [{"letter": LABELS[i], "confidence": float(probabilities[i] * 100)} for i in top3_idx]

    return jsonify({
        "prediction": idx,
        "confidence": confidence,
        "top3": top3
    })


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """
    Run full model evaluation on the stored test split.
    Uses group-based split data (no data leakage).
    Returns accuracy, precision, recall, f1, mAP, confusion matrix,
    classification report, and per-letter accuracy.
    """
    try:
        x_test = eval_x_test
        y_test = eval_y_test

        # Predictions
        y_pred = model.predict(x_test)
        y_proba = model.predict_proba(x_test)

        # Core metrics (macro averaged)
        accuracy = float(accuracy_score(y_test, y_pred))
        precision = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        recall = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))

        # mAP (One-vs-Rest)
        class_labels = np.unique(y_test)
        y_test_bin = label_binarize(y_test, classes=class_labels)
        map_score = float(average_precision_score(y_test_bin, y_proba, average="macro"))

        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred, labels=list(range(26)))
        cm_list = cm.tolist()

        # Classification Report (as dict)
        report = classification_report(
            y_test,
            y_pred,
            target_names=[LABELS[i] for i in range(26)],
            output_dict=True,
            zero_division=0
        )

        # Per-letter accuracy
        per_letter = []
        for i in range(26):
            mask = y_test == i
            if mask.sum() > 0:
                letter_acc = float(accuracy_score(y_test[mask], y_pred[mask]))
            else:
                letter_acc = 0.0
            per_letter.append({
                "letter": LABELS[i],
                "accuracy": letter_acc,
                "support": int(mask.sum())
            })

        return jsonify({
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "mAP": map_score,
            "confusion_matrix": cm_list,
            "classification_report": report,
            "per_letter": per_letter,
            "test_size": int(len(y_test)),
            "labels": list(LABELS),
            "split_source": SPLIT_FILE or "data.pickle (fallback)"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs", methods=["POST"])
def save_log():
    """Save a detection/testing log entry."""
    try:
        entry = request.json
        entry["timestamp"] = datetime.now().isoformat()

        log_file = os.path.join(LOGS_DIR, "detection_logs.json")

        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)

        logs.append(entry)

        # Keep last 500 entries
        logs = logs[-500:]

        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)

        return jsonify({"status": "ok", "count": len(logs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs", methods=["GET"])
def get_logs():
    """Retrieve stored detection logs."""
    log_file = os.path.join(LOGS_DIR, "detection_logs.json")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
        return jsonify(logs)
    return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
