from utils.file_utils import ensure_dir, load_metadata
from utils.pdf_utils import extract_text_from_pdf
from utils.download_utils import download_paper
from utils.parquet_utils import get_last_processed_id, save_to_parquet
from config import METADATA_DIR, DATA_DIR, SAVE_THRESHOLD

import os 
import re
import time


def process_papers():
    # Iterate through each JSON file in the METADATA_DIR
    for json_file in os.listdir(METADATA_DIR):
        
        if not json_file.endswith(".json"):
            continue
        
        category = os.path.splitext(json_file)[0]
        
        # Path to the JSON metadata file
        category_path = os.path.join(METADATA_DIR, json_file)
        
        # Load metadata from the JSON file
        metadata = load_metadata(category_path)
        
        # Get the last processed arXiv ID from parquet files (if any)
        last_processed_arxiv_id = get_last_processed_id(category) 
        
        # Initialize an empty list to store the current batch of data
        data_chunk = []
        
        # Define the path to the directory where the papers' PDFs will be saved
        category_data_dir = os.path.join(DATA_DIR, category)
        ensure_dir(category_data_dir)

        # Flag to resume processing from the last processed paper
        resume_processing = last_processed_arxiv_id is None 
    

        # Iterate through each paper in the metadata
        for i, paper in enumerate(metadata):            
            # Extract the arXiv ID from the PDF link
            arxiv_id_match = re.search(r"(\d{4}\.\d+)", paper['pdf_link'])
            
            if not arxiv_id_match:
                legacy_match = re.search(r"[a-z\-]+\/(\d{6,})", paper['pdf_link'])
                
                if legacy_match:
                    arxiv_id = legacy_match.group(1)
                else:
                    print(f"⚠ Skipping paper {paper['title']} (Invalid ArXiv ID)")
                    continue
            else:
                arxiv_id = arxiv_id_match.group(0)
           
            if not resume_processing:
                if arxiv_id == last_processed_arxiv_id:
                    print(f"Found last processed paper {arxiv_id}, resuming_downloads...")
                    resume_processing = True
                continue

            # Define the path for saving the downloaded PDF
            pdf_filename = f"{arxiv_id}.pdf"
            pdf_path = os.path.join(category_data_dir, pdf_filename)

            # Download the paper using the arXiv ID and save to the specified directory
            if not download_paper(paper['pdf_link'], arxiv_id, category_data_dir):
                continue  # Skip if download fails
            
            # Extract text from the downloaded PDF
            pdf_text = extract_text_from_pdf(pdf_path)
            if not pdf_text:
                print(f"⚠ Skipping {arxiv_id} (Empty PDF text)")
                os.remove(pdf_path)
                print(f"🗑 Deleted {pdf_filename}")
                continue
            
            data_chunk.append({
                "arxiv_id": arxiv_id,
                "title": paper["title"],
                "authors": ", ".join(paper["authors"]),
                "year": paper["published_year"],
                "category": category,
                "summary": paper["summary"], 
                "pdf_content": pdf_text, 

            })

            # Print progress
            print(i)
            
            # Delete the PDF after processing
            os.remove(pdf_path)
            print(f"🗑 Deleted {pdf_filename}")

            # Save data to Parquet every SAVE_THRESHOLD papers
            if len(data_chunk) >= SAVE_THRESHOLD:
                save_to_parquet(category, data_chunk)
                data_chunk = []  # Reset the data chunk
        

            time.sleep(1)

        # Final save if there is remaining data
        if data_chunk:
            save_to_parquet(category, data_chunk)
    
    print("✅ All papers processed.")


if __name__ == "__main__":
    process_papers()
