import os
import pandas as pd
from collections import defaultdict

# Dictionary to track summaries and associated (arxiv_id, file)
summary_to_entries = defaultdict(list)

# Get all .parquet files in the current directory
parquet_files = [f for f in os.listdir() if f.endswith(".parquet")]

# Check for repeated summaries across files
for file in parquet_files:
    try:
        df = pd.read_parquet(file)
        if "summary" in df.columns:
            for _, row in df.iterrows():
                summary = row["summary"]
                arxiv_id = row.get("arxiv_id", "N/A")
                summary_to_entries[summary].append((arxiv_id, file))
        else:
            print(f"⚠️ Skipping {file}: 'summary' column not found.")
    except Exception as e:
        print(f"⚠️ Error reading {file}: {e}")

# Filter to only repeated summaries
repeated_summaries = {
    summary: entries
    for summary, entries in summary_to_entries.items()
    if len(entries) > 1
}

# Print results
if repeated_summaries:
    print("\n🔁 Repeated summaries found across files:\n")
    for summary, entries in repeated_summaries.items():
        print(f"Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
        for arxiv_id, file in entries:
            print(f"  - ID: {arxiv_id} | File: {file}")
        print()
else:
    print("\n✅ No repeated summaries found across files.")
