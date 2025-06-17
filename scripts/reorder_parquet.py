import os
import pandas as pd
from collections import defaultdict
import re
import zipfile


def unzip_files(directory: str):
    """
    Unzip all .zip files in the given directory.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".zip"):
            zip_path = os.path.join(directory, filename)
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(directory)
            print(f"Extracted {zip_path} into {directory}")


# unzip_files(".")


# Step 1: Group files by category prefix (e.g., math.AT from math.AT_1.parquet)
category_files = defaultdict(list)
pattern = re.compile(r"^(.*)_\d+\.parquet$")

for filename in os.listdir("."):
    if filename.endswith(".parquet"):
        match = pattern.match(filename)
        if match:
            category = match.group(1)
            category_files[category].append(filename)

# Step 2: Process each category
for category, files in category_files.items():
    print(f"\n📁 Processing category: {category}")

    files.sort()  # Ensure file order is preserved

    # Show individual file row counts
    for file in files:
        try:
            df = pd.read_parquet(file)
            print(f"  - {file:<30} ➤ {len(df)} rows")
        except Exception as e:
            print(f"  - {file:<30} ⚠️ Error reading file: {e}")

    # Read and concatenate all dataframes for this category
    dfs = [pd.read_parquet(file) for file in files]
    full_df = pd.concat(dfs, ignore_index=True)

    # Step 3: Chunk into 500-row pieces
    total_rows = len(full_df)
    num_chunks = (total_rows + 499) // 500

    for i in range(num_chunks):
        chunk = full_df.iloc[i*500:(i+1)*500]
        output_filename = f"{category}_{i+1}.parquet"
        chunk.to_parquet(output_filename, index=False)
        print(f"    ➤ Saved: {output_filename} ({len(chunk)} rows)")

print("\n✅ Done reorganizing all categories.")
