import fitz

def extract_text_from_pdf(pdf_path):
    """
    This function opens the PDF file located at the given path and extracts the text from all pages.

    Args:
        pdf_path (str): The file path to the PDF from which to extract text.

    Returns:
        str: The extracted text from the PDF. Returns None if an error occurs.
    """
    try:
        doc = fitz.open(pdf_path)
        return "\n".join([page.get_text("text") for page in doc])
    
    except Exception as e:
        print(f"⚠ Error reading {pdf_path}: {e}")
        return None