import os
import re
import pandas as pd

MAX_ENTRIES_PER_PARQUET = 500


def get_latest_parquet_file(category):
    """
    Retrieves the most recent Parquet file for a given category.
    
    Args:
        category (str): The category name used as the prefix for Parquet files.
        
    Returns:
        str: The filename of the most recent Parquet file for the category.
    """
    existing_files = [f for f in os.listdir() if f.startswith(f"{category}") and f.endswith(".parquet")]
    if not existing_files:
        return f"{category}_1.parquet"
    existing_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    return existing_files[-1]


def save_to_parquet(category, data_chunk):
    """
    Saves a chunk of data to a Parquet file for a given category. If a Parquet file for the category already exists, the function appends the new data
    to it, provided the total number of records does not exceed the specified limit.
    
    Args:
        category (str): The category name used to name the Parquet file.
        data_chunk (list of dict): A list of data entries to be saved to the Parquet file.
    """
    
    parquet_file = get_latest_parquet_file(category)

    # Load existing data if file exists
    if os.path.exists(parquet_file):
        df_existing = pd.read_parquet(parquet_file, engine="pyarrow")
        if len(df_existing) >= MAX_ENTRIES_PER_PARQUET:
            match = re.search(r"_(\d+)\.parquet", parquet_file)
            idx = int(match.group(1))

            df_new = pd.DataFrame(data_chunk)
            parquet_file = f"{category}_{idx+1}.parquet"
            df_new.to_parquet(parquet_file, engine="pyarrow", compression="snappy")
        else:
            df_new = pd.DataFrame(data_chunk)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_parquet(parquet_file, engine="pyarrow", compression="snappy")
    else:
        df_new = pd.DataFrame(data_chunk)
        df_new.to_parquet(parquet_file, engine="pyarrow", compression="snappy")
        
    print(f"💾 Successfully saved {len(data_chunk)} new records to {parquet_file}")


def get_last_processed_id(category):
    """
    Retrieves the last processed arXiv ID from the latest Parquet file for a given category.
    
    Args:
        category (str): The category name used to identify the Parquet file.
        
    Returns:
        str or None: The last processed arXiv ID, or None if no file exists or if the file is empty.
    """
    parquet_file = get_latest_parquet_file(category)

    if not os.path.exists(parquet_file):
        return None
    
    try:
        # Load the Parquet file
        df = pd.read_parquet(parquet_file, engine="pyarrow")
        
        # If the DataFrame is empty, return None to indicate no processed records
        if df.empty:
            return None
        
        # Get the arXiv ID of the last processed record
        last_id = df.iloc[-1]["arxiv_id"]
        print(f"🔄 Resuming from last processed paper: {last_id}")
        return last_id
    except Exception as e:
        # If there is an error reading the file, print the error and return None
        print(f"⚠ Error reading Parquet file {parquet_file}: {e}")
        return None
