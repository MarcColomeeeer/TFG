import os

def ensure_dir(path):
    """
    Ensures that the directory at the given path exists. If the directory does not exist, it will be created.
    
    Args:
        path (str): The path of the directory to check and create if necessary.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def find_downloaded_pdf(directory, arxiv_id):
    """
    Searches for a PDF file in the given directory that starts with the specified arXiv ID.
    
    Args:
        directory (str): The directory to search in.
        arxiv_id (str): The arXiv ID that the filename should start with.
        
    Returns:
        str: The filename of the matching PDF if found, otherwise None.
    """
    for filename in os.listdir(directory):
        if filename.startswith(arxiv_id) and filename.endswith(".pdf"):
            return filename
    return None


def rename_file(old_path, new_path):
    """
    Renames a file from old_path to new_path.
    
    Args:
        old_path (str): The current path of the file to rename.
        new_path (str): The new path for the renamed file.
        
    Raises:
        Exception: If an error occurs during renaming the file.
    """
    try:
        os.rename(old_path, new_path)
        print(f"📂 Renamed {old_path} → {new_path}")
    except Exception as e:
        print(f"❌ Error renaming file {old_path} → {new_path}: {e}")

import json


def load_metadata(json_file):
    """
    Loads metadata from a JSON file.

    Args:
        json_file (str): The path to the JSON file containing metadata.
        
    Returns:
        dict or list: The parsed metadata from the JSON file.
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Error loading metadata from {json_file}: {e}")
        return None
