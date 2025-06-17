import os
import pandas as pd

# Directory containing the parquet chunks
papers_dir = "papers"

# Get list of parquet files
parquet_files = sorted([
    f for f in os.listdir(papers_dir)
    if f.endswith(".parquet")
])

# Read and combine all the DataFrames
dfs = []
for i, f in enumerate(parquet_files, 1):
    full_path = os.path.join(papers_dir, f)
    print(f"[{i}/{len(parquet_files)}] 📄 Reading {full_path}")
    df = pd.read_parquet(full_path)
    dfs.append(df)

# Concatenate all into one DataFrame
df_papers = pd.concat(dfs, ignore_index=True)

print(df_papers.columns)
print(f"\n✅ Combined DataFrame created with {len(df_papers):,} rows.")

# Optional: save combined result
# df_papers.to_parquet("papers_combined.parquet", index=False)
