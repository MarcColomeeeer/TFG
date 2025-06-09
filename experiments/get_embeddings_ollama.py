import os
import pandas as pd
import ollama

# === Configuration ===
EMBED_MODEL = 'llama3.1'        # 🔁 Change model name here
MAX_PER_FILE = 10000            # Max rows per output file
SAVE_EVERY = 500                # Save after this many rows
COLUMNS_TO_EMBED = ['title', 'summary']  # Columns to process
COLUMN_DATA_DIR = '../data/experiment_8'
EMBED_PREFIX = f"embeddings.{EMBED_MODEL}"


def extract_embedding(text):
    response = ollama.embed(model=EMBED_MODEL, input=text)
    return response['embeddings']


for column in COLUMNS_TO_EMBED:
    print(f"\n🚀 Starting embedding generation for column: '{column}'")

    file_index = 1
    total_saved = 0
    current_file_results = []

    column_path = os.path.join(COLUMN_DATA_DIR, f"{column}.parquet")
    if not os.path.exists(column_path):
        print(f"❌ Column file '{column_path}' not found. Skipping.")
        continue

    col_data = pd.read_parquet(column_path)

    # Detect where to resume
    while True:
        filename = f"{EMBED_PREFIX}.{column}_{file_index}.parquet"
        if os.path.exists(filename):
            existing = pd.read_parquet(filename)
            total_saved += len(existing)
            file_index += 1
        else:
            break

    print(f"🛠️ Resuming from row {total_saved} for column '{column}'")

    for i in range(total_saved, len(col_data)):
        text = col_data.iloc[i][column]

        try:
            embedding = extract_embedding(text)
        except Exception as e:
            print(f"⚠️ Skipping row {i} due to error: {e}")
            continue

        current_file_results.append(embedding)
        print(f"✅ Processed row {i} for column '{column}'")

        if len(current_file_results) % SAVE_EVERY == 0:
            output_file = f"{EMBED_PREFIX}.{column}_{file_index}.parquet"
            pd.DataFrame(current_file_results).to_parquet(output_file, index=False)
            print(f"💾 Checkpoint saved: {output_file}")

        if len(current_file_results) >= MAX_PER_FILE:
            output_file = f"{EMBED_PREFIX}.{column}_{file_index}.parquet"
            pd.DataFrame(current_file_results).to_parquet(output_file, index=False)
            print(f"📁 Finalized file {output_file} with {len(current_file_results)} rows")
            file_index += 1
            current_file_results = []

    if current_file_results:
        output_file = f"{EMBED_PREFIX}.{column}_{file_index}.parquet"
        pd.DataFrame(current_file_results).to_parquet(output_file, index=False)
        print(f"✅ Final save: {output_file} with {len(current_file_results)} rows")

print("\n🎉 All embeddings generated and saved successfully.")
