import os
import pandas as pd
from utils.connections_utils import get_connection
from utils.populate_tables_utils import populate_all_tables
from utils.create_tables_utils import create_all_tables

def main():
    """
    Main script to populate the database accordingly.
    """

    # Define the data directory
    data_dir = "/data"

    # Step 1: Connect to the database
    conn = get_connection()

    # Step 2: Create tables
    create_all_tables()

    # Step 3: Walk through all subdirectories and process .parquet files
    for root, _, files in os.walk(data_dir):
        for filename in files:
            if filename.endswith(".parquet"):
                parquet_path = os.path.join(root, filename)
                print(f"📄 Processing {parquet_path}...")

                paper_df = pd.read_parquet(parquet_path)
                paper_df["dim1"] = None
                paper_df["dim2"] = None

                populate_all_tables(conn, paper_df)

    # Step 4: Close the connection
    conn.close()
    print("✅ All files processed and database populated successfully.")

if __name__ == "__main__":
    main()