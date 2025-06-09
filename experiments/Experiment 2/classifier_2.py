from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

import pandas as pd
import numpy as np

# --- Load Data ---
def load_embeddings_and_labels(category):
    emb = pd.read_parquet(f"embeddings.summary.{category}.parquet")
    split = pd.read_parquet(f"split.{category}.parquet")
    labels = pd.read_parquet(f"category.{category}.parquet")
    return emb, split, labels

df_8, split_8, labels_8 = load_embeddings_and_labels(8)
df_11, split_11, labels_11 = load_embeddings_and_labels(11)

# --- Combine ---
combined_vectors = pd.concat([df_8, df_11], ignore_index=True)
combined_vectors = np.array(combined_vectors["0"].to_list())

labels = pd.concat([labels_8, labels_11], ignore_index=True)
splits = pd.concat([split_8, split_11], ignore_index=True)

# --- Train/Test Split ---
train_idx = splits[splits["split"] == "train"].index
test_idx = splits[splits["split"] == "test"].index

X_train = combined_vectors[train_idx]
X_test = combined_vectors[test_idx]

y_train = labels.iloc[train_idx]
y_test = labels.iloc[test_idx]

# --- Encode Labels ---
encoder = LabelEncoder()
y_train_enc = encoder.fit_transform(y_train)
y_test_enc = encoder.transform(y_test)

# --- Train SVM ---
model = SVC(kernel="linear", C=1)
model.fit(X_train, y_train_enc)

# --- Evaluate ---
y_pred = model.predict(X_test)

acc = accuracy_score(y_test_enc, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(
    y_test_enc, y_pred, average="weighted"
)
conf_matrix = confusion_matrix(y_test_enc, y_pred)

# --- Results ---
print("\n📊 Evaluation Metrics")
print(f"Accuracy : {acc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-Score : {f1:.4f}")

print("\n🧩 Confusion Matrix")
conf_df = pd.DataFrame(
    conf_matrix,
    index=encoder.classes_,
    columns=encoder.classes_
)
print(conf_df)
