import pandas as pd
import os

# Get all .parquet files in the current directory
parquet_files = [f for f in os.listdir('../data/experiment_8') if f.endswith('.parquet')]

for filename in parquet_files:
    column_name = os.path.splitext(os.path.basename(filename))[0]

    try:
        df = pd.read_parquet(filename)

        if column_name not in df.columns:
            print(f"⚠️  Skipping '{filename}': Column '{column_name}' not found.")
            continue

        texts = df[column_name].dropna()
        total_words = texts.apply(lambda x: len(str(x).split())).sum()
        total_chars = texts.apply(lambda x: len(str(x))).sum()
        num_rows = len(texts)

        if num_rows == 0:
            print(f"⚠️  Skipping '{filename}': No valid rows.")
            continue

        avg_words = total_words / num_rows
        avg_chars = total_chars / num_rows

        print(f"\n📄 File: {filename}")
        print(f"🔢 Total rows processed: {num_rows}")
        print(f"✍️  Total words: {total_words}")
        print(f"🔠 Total characters: {total_chars}")
        print(f"📊 Average words per row: {avg_words:.2f}")
        print(f"📊 Average characters per row: {avg_chars:.2f}")

    except Exception as e:
        print(f"❌ Error processing '{filename}': {e}")
