from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

import pandas as pd
import numpy as np

LABELS_PATH = "../../data/experiment_8/category.parquet"
SPLIT_PATH = "../../data/experiment_8/split.parquet"

# --- Load Embeddings ---
summary_df = pd.read_parquet("embeddings.summary.parquet")
title_df = pd.read_parquet("embeddings.title.parquet")
text_df = pd.read_parquet("embeddings.text_wo_ref_wo_num_wo_short.parquet")

# --- Combine embeddings ---
combined_df = np.concatenate([summary_df, title_df, text_df], axis=1)
# combined_df = summary_df + title_df + text_df

# --- Load Metadata ---
labels = pd.read_parquet(LABELS_PATH)
split_info = pd.read_parquet(SPLIT_PATH)

# --- Split into Train/Test ---
train_idx = split_info[split_info["split"] == "train"].index.tolist()
test_idx = split_info[split_info["split"] == "test"].index.tolist()

X_train = combined_df[train_idx]
X_test = combined_df[test_idx]
y_train = labels.iloc[train_idx]
y_test = labels.iloc[test_idx]

# --- Encode Labels ---
label_encoder = LabelEncoder()
y_train_enc = label_encoder.fit_transform(y_train)
y_test_enc = label_encoder.transform(y_test)

# --- Train Model ---
print("🧠 Training SVM classifier...")
svm_model = SVC(kernel="linear", C=1)
svm_model.fit(X_train, y_train_enc)

# --- Predict & Evaluate ---
y_pred = svm_model.predict(X_test)
accuracy = accuracy_score(y_test_enc, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(y_test_enc, y_pred, average="weighted")
conf_matrix = confusion_matrix(y_test_enc, y_pred)

# --- Report Results ---
print("\n📊 Evaluation Results")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-Score : {f1:.4f}")

print("\n🧩 Confusion Matrix:")
conf_df = pd.DataFrame(conf_matrix, index=label_encoder.classes_, columns=label_encoder.classes_)
print(conf_df)
