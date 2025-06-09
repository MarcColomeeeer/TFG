from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

import pandas as pd
import numpy as np

# --- Configuration ---
EMBEDDING_PATH =  "embeddings.summary.parquet"
LABELS_PATH = "../../data/experiment_8/category.parquet"
SPLIT_PATH = "../../data/experiment_8/split.parquet"

# --- Load Data ---
print("🚀 Loading embeddings and metadata...")
df = pd.read_parquet(EMBEDDING_PATH)

# Convert Series of lists into a NumPy array
embedding_array = np.array(df.iloc[:, 0].tolist())

# Load labels and split metadata
labels = pd.read_parquet(LABELS_PATH)
split_info = pd.read_parquet(SPLIT_PATH)

# --- Train/Test Split ---
train_idx = split_info[split_info["split"] == "train"].index
test_idx = split_info[split_info["split"] == "test"].index

X_train = embedding_array[train_idx]
X_test = embedding_array[test_idx]
y_train = labels.iloc[train_idx]
y_test = labels.iloc[test_idx]

# --- Label Encoding ---
label_encoder = LabelEncoder()
y_train_enc = label_encoder.fit_transform(y_train)
y_test_enc = label_encoder.transform(y_test)

# --- Train SVM ---
print("🧠 Training linear SVM...")
model = SVC(kernel="linear", C=1)
model.fit(X_train, y_train_enc)

# --- Evaluate ---
print("📊 Evaluating model...")
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test_enc, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(y_test_enc, y_pred, average="weighted")
conf_matrix = confusion_matrix(y_test_enc, y_pred)

# --- Results ---
print("\n✅ Evaluation Metrics")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-Score : {f1:.4f}")

print("\n🧩 Confusion Matrix")
conf_df = pd.DataFrame(conf_matrix, index=label_encoder.classes_, columns=label_encoder.classes_)
print(conf_df)
