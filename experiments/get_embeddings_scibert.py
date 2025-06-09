import os
import torch
import pandas as pd

from transformers import AutoTokenizer, AutoModel

# --- Configuration ---
LOCAL_MODEL_PATH = './sciBERT'
DATA_PATH = '../../data/experiments/data.parquet'
COLUMNS_TO_PROCESS = ['summary', 'title']
CHUNK_SIZE = 500


# --- Load Model & Tokenizer ---
tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
model = AutoModel.from_pretrained(LOCAL_MODEL_PATH)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# --- Embedding Extraction ---
def extract_embedding(text):
    inputs = tokenizer(
        text,
        return_tensors='pt',
        truncation=True,
        padding=True,
        max_length=512
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    cls_embedding = outputs.last_hidden_state[:, 0, :]
    return cls_embedding.squeeze().cpu().numpy().tolist()


# --- Embedding Generation ---
def process_column(df, column, output_name, chunk_size=CHUNK_SIZE):
    output_file = f"embeddings.scibert.{output_name}.parquet"

    if os.path.exists(output_file):
        existing = pd.read_parquet(output_file)
        start_idx = len(existing)
        embeddings = existing.values.tolist()
        print(f"🛠️ Resuming from row {start_idx} for column '{column}'")
    else:
        start_idx = 0
        embeddings = []
        print(f"🆕 Starting embedding generation for column '{column}'")

    for idx in range(start_idx, len(df)):
        text = df.iloc[idx][column]
        embedding = extract_embedding(text)
        embeddings.append(embedding)
        print(f"✅ Processed row {idx} in column '{column}'")

        if len(embeddings) % chunk_size == 0:
            save_embeddings(embeddings, output_file)

    save_embeddings(embeddings, output_file)


# --- Save Function ---
def save_embeddings(embeddings, output_file):
    df = pd.DataFrame(embeddings)
    df.to_parquet(output_file, index=False)
    print(f"💾 Saved {len(embeddings)} embeddings to '{output_file}'")


# --- Main Execution ---
if __name__ == "__main__":
    df = pd.read_parquet(DATA_PATH)

    for column in COLUMNS_TO_PROCESS:
        print(f"\n🚀 Processing column: '{column}'")
        process_column(df, column, column)

    print("\n🎉✅ All embeddings generated and saved.")
