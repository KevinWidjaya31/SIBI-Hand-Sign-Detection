import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# Load dataset
data_dict = pickle.load(open('./data.pickle', 'rb'))
data = data_dict['data']
labels = data_dict['labels']

# Pastikan semua sample punya panjang sama
max_len = max(len(d) for d in data)
data_fixed = [d + [0]*(max_len - len(d)) for d in data]  # padding dengan 0
X = np.array(data_fixed)
y = np.array([int(l) for l in labels])

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Definisikan semua model
models = {
    "XGBoost": XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.05, use_label_encoder=False, eval_metric="mlogloss"),
    "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42),
    "SVM": SVC(kernel='linear', probability=True),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "Logistic Regression": LogisticRegression(max_iter=1000)
}

# Latih semua model dan simpan akurasi
accuracy_scores = {}
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"{name} Accuracy: {acc*100:.2f}%\n")
    accuracy_scores[name] = acc

# Buat grafik perbandingan akurasi
plt.figure(figsize=(10,6))
plt.bar(accuracy_scores.keys(), [v*100 for v in accuracy_scores.values()], color='skyblue')
plt.ylabel("Accuracy (%)")
plt.title("Comparison of Classifier Accuracy")
plt.ylim(0, 100)
plt.show()
