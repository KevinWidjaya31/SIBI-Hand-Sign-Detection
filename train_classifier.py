import pickle
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ===============================
# 1. Load Dataset
# ===============================
data_dict = pickle.load(open('./data.pickle', 'rb'))
data = np.asarray(data_dict['data'])
labels = np.asarray([int(label) for label in data_dict['labels']])

# ===============================
# 2. Split Dataset (Train / Test / Validation)
# ===============================
x_train, x_temp, y_train, y_temp = train_test_split(
    data, labels, test_size=0.3, stratify=labels, random_state=42
)

x_val, x_test, y_val, y_test = train_test_split(
    x_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)

# ===============================
# 3. Define XGBoost Model
# ===============================
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='multi:softprob',
    num_class=len(np.unique(labels)),
    eval_metric="mlogloss",
    early_stopping_rounds=10,
    random_state=42
)

# ===============================
# 4. Train Model (Early Stopping Pakai Validation)
# ===============================
model.fit(
    x_train,
    y_train,
    eval_set=[(x_val, y_val)],
    verbose=True
)

# ===============================
# 5. Predict
# ===============================
y_predict = model.predict(x_test)

# ===============================
# 6. Accuracy
# ===============================
score = accuracy_score(y_test, y_predict)
print(f'\nAccuracy: {score * 100:.2f}%')

# ===============================
# 7. Classification Report
# ===============================
print("\nClassification Report:\n")
print(classification_report(
    y_test,
    y_predict,
    target_names=[chr(i+65) for i in range(26)]
))

# ===============================
# 8. Confusion Matrix (A–Z)
# ===============================
cm = confusion_matrix(y_test, y_predict)

plt.figure(figsize=(12, 10))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=[chr(i+65) for i in range(26)],
    yticklabels=[chr(i+65) for i in range(26)]
)

plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix (A-Z)')
plt.show()

# ===============================
# 9. Feature Importance
# ===============================
plt.figure(figsize=(10, 8))
xgb.plot_importance(model, max_num_features=15)
plt.title("Top 15 Most Important Features")
plt.show()

# ===============================
# 10. Save Model
# ===============================
with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)