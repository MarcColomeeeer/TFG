import os
import zipfile
import re
from collections import defaultdict

def zip_parquet_files(directory: str):
    """
    Zip .parquet files in the given directory by category prefix.
    """
    
    category_files = defaultdict(list)
    pattern = re.compile(r"^(.*)_\d+\.parquet$")

    for filename in os.listdir(directory):
        if filename.endswith(".parquet"):
            match = pattern.match(filename)
            if match:
                category = match.group(1)
                category_files[category].append(filename)

    for category, files in category_files.items():
        zip_path = os.path.join(directory, f"{category}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                zipf.write(os.path.join(directory, file), arcname=file)
        print(f"Created {zip_path} with {len(files)} files.")


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

# zip_parquet_files(".")
unzip_files(".")
