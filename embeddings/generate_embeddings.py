import pandas as pd
import ollama
import os
import time

# Define constants
COLUMNS_TO_EMBED = ['title', 'summary']
CHUNK_SIZE = 10_000
EMBEDDING_MODEL = 'llama3.1'

def extract_embedding(text, retries=3, delay=0):
    for attempt in range(retries):
        try:
            response = ollama.embed(model=EMBEDDING_MODEL, input=text)
            return response['embeddings']
        except Exception as e:
            print(f"⚠️ Retry {attempt + 1}/{retries} failed: {e}")
            time.sleep(delay)
    raise RuntimeError(f"❌ Failed to embed after {retries} attempts.")

# Ensure embeddings directory exists
os.makedirs('embeddings', exist_ok=True)

# Collect lengths of all eligible parquet files
category_lengths = []
for file in os.listdir('data'):
    if file.endswith(".parquet") and file.startswith("data."):
        file_path = os.path.join('data', file)
        try:
            df = pd.read_parquet(file_path, columns=['arxiv_id'])  # lightweight read
            category_lengths.append((file, len(df)))
        except Exception as e:
            print(f"❌ Could not read {file}: {e}")

# Sort files by size (ascending)
sorted_category_files = sorted(category_lengths, key=lambda x: x[1])

# Process files
for category_file, file_length in sorted_category_files:
    category_file_path = os.path.join('data', category_file)
    print(f"\n🚀 Starting embedding generation for category: {category_file} ({file_length} rows)")
    category_data = pd.read_parquet(category_file_path)

    for column in COLUMNS_TO_EMBED:
        base_output = f"embeddings.{category_file.replace('.parquet', '')}_{column}"
        output_files = sorted([
            f for f in os.listdir('embeddings') if f.startswith(base_output) and f.endswith('.parquet')
        ])

        # Count already processed rows
        total_done = 0
        for fname in output_files:
            try:
                df_chunk = pd.read_parquet(os.path.join('embeddings', fname))
                total_done += len(df_chunk)
            except Exception as e:
                print(f"⚠️ Skipping unreadable file {fname}: {e}")

        if total_done >= file_length:
            print(f"⏭️ Skipping '{column}' in '{category_file}' — all embeddings exist.")
            continue

        print(f"\n  🧠 Generating embeddings for column: {column}")
        chunk = []
        chunk_index = len(output_files) + 1

        for i in range(total_done, file_length):
            text = category_data.iloc[i][column]

            try:
                embedding = extract_embedding(text)
                chunk.append(embedding)
                print(f"    ✅ Row {i} done for '{column}' in '{category_file}'")
            except Exception as e:
                print(f"⚠️ Skipping row {i} due to error: {e}")
                continue

            if len(chunk) >= CHUNK_SIZE:
                output_path = os.path.join('embeddings', f"{base_output}_{chunk_index}.parquet")
                pd.DataFrame(chunk).to_parquet(output_path, index=False)
                print(f"    💾 Saved chunk {chunk_index} to {output_path}")
                chunk = []
                chunk_index += 1

        if chunk:
            output_path = os.path.join('embeddings', f"{base_output}_{chunk_index}.parquet")
            pd.DataFrame(chunk).to_parquet(output_path, index=False)
            print(f"    💾 Saved final chunk {chunk_index} to {output_path}")

print("\n🎉 All embeddings processed and saved for all categories.")
