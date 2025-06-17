import pandas as pd
import os
import re
from collections import defaultdict

# Prepare dictionary to group DataFrames by category
category_frames = defaultdict(list)

# Pattern to extract category prefix from filenames like econ.TH_1.parquet
pattern = re.compile(r"^(.*)_\d+\.parquet$")

# Loop over all .parquet files in the current directory
for file in os.listdir():
    if file.endswith(".parquet"):
        match = pattern.match(file)
        if match:
            category = match.group(1)
            try:
                df = pd.read_parquet(file)
                if all(col in df.columns for col in ["arxiv_id", "summary", "title"]):
                    category_frames[category].append(df[["arxiv_id", "summary", "title"]])
                    print(f"✅ Included: {file} in category {category}")
                else:
                    print(f"⚠️ Skipping {file}: missing required columns")
            except Exception as e:
                print(f"❌ Error reading {file}: {e}")
        else:
            print(f"⚠️ Skipping {file}: filename doesn't match expected pattern")

# Save one file per category
for category, frames in category_frames.items():
    combined_df = pd.concat(frames, ignore_index=True)
    output_file = f"data.{category}.parquet"
    combined_df.to_parquet(output_file, index=False)
    print(f"💾 Saved {len(combined_df)} rows to '{output_file}'")

if not category_frames:
    print("⚠️ No valid data found to combine.")
