import subprocess
import os

def download_paper(url, arxiv_id, save_dir):
    """
    Downloads an arXiv paper using curl.

    Args:
        arxiv_id (str): The arXiv ID (e.g. '1507.00123' or 'hep-th/9901001')
        save_dir (str): Directory where the PDF should be saved

    Returns:
        bool: True if successful, False otherwise
    """
    # Ensure save_dir exists
    os.makedirs(save_dir, exist_ok=True)

    # Replace slashes in legacy IDs to form valid filenames
    output_path = os.path.join(save_dir, f"{arxiv_id}.pdf")

    try:
        result = subprocess.run(
            ["curl", "-L", url, "-o", output_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ Downloaded {arxiv_id} to {output_path}")
            return True
        else:
            print(f"❌ Failed to download {arxiv_id}: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False
