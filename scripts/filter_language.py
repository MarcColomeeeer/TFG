import re
import pandas as pd
import glob

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException



# Process all .parquet files in a single loop
for file_path in glob.glob("*.parquet"):
    print(f"\nProcessing: {file_path}")
    df = pd.read_parquet(file_path)
    if "pdf_content" not in df.columns:
        print(f"⚠️ Skipping {file_path}: Missing 'pdf_content' column.")
        continue

    indices_to_drop = []

    for i, content in enumerate(df['pdf_content']):
        try:
            lang = detect(content)
            if lang != 'en':
                print(f"Row {i}: not English ({lang}) — will drop")
                indices_to_drop.append(i)
                continue
        except LangDetectException:
            print(f"Row {i}: language detection failed — will drop")
            indices_to_drop.append(i)
            continue


    # Drop invalid rows
    df_clean = df.drop(indices_to_drop, axis=0)
    df_clean.to_parquet(file_path)
    print(f"✔ {file_path} updated — dropped {len(indices_to_drop)} rows")