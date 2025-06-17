import os
import numpy as np
import pandas as pd
import umap
from sklearn.manifold import TSNE


embeddings_dir = "embeddings"

# Known dimensions
TOTAL_ROWS = 1_331_680
VECTOR_DIM = 4096

# Preallocate the big array
print(f"🧠 Preallocating array of shape ({TOTAL_ROWS}, {VECTOR_DIM})...")
X = np.empty((TOTAL_ROWS, VECTOR_DIM), dtype=np.float32)

parquet_files = sorted([f for f in os.listdir(embeddings_dir) if f.endswith(".parquet")])
print(f"🔍 Found {len(parquet_files)} parquet files.")

current_row = 0
for i, filename in enumerate(parquet_files, 1):
    full_path = os.path.join(embeddings_dir, filename)
    print(f"[{i}/{len(parquet_files)}] 📥 Loading file: {filename}")
    df = pd.read_parquet(full_path)

    if "0" not in df.columns:
        raise ValueError(f"Column '0' with embeddings not found in {filename}.")

    n_rows = len(df)
    print(f"    Processing {n_rows} rows...")

    X[current_row:current_row+n_rows, :] = np.vstack([np.array(row, dtype=np.float32) for row in df["0"].values])
    current_row += n_rows

    del df


tsne = TSNE(
    n_components=2,
    perplexity=1200,
    learning_rate=1000,
    max_iter=3000,
    init='pca',
    method='barnes_hut',
    random_state=42
)

Z = tsne.fit_transform(X)

# Save UMAP output
df_Z = pd.DataFrame(Z, columns=["dim_1", "dim_2"])
output_file = os.path.join(embeddings_dir, "TSNE.parquet")
df_Z.to_parquet(output_file, index=False)
print(f"💾 TSNE output saved to '{output_file}' with {len(df_Z)} rows.")
