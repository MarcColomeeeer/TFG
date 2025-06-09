import re
import pandas as pd

# Define a set of meaningful 1- and 2-letter words to keep
meaningful_short_words = {
    "a", "an", "am", "as", "at", "be", "by", "do", "go", "he", "hi",
    "if", "in", "is", "it", "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we", ".", "(", ")",
    "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0.", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "et", "\n"
}

# Add numbers from 0 to 99 and -1 to -9 to the set
meaningful_short_words.update({str(i) for i in range(100)})  # Add numbers 0 to 99
meaningful_short_words.update({str(i) for i in range(-1, -10, -1)})  # Add numbers -1 to -9


def clean_short_words(text):
    """
    Cleans the input text by removing short words (length <= 2), except for a predefined list of meaningful short words, while preserving newlines.
    """
    lines = text.split("\n")
    cleaned_lines = [
        " ".join([word for word in line.split() if len(word) > 2 or word in meaningful_short_words])
        for line in lines
    ]
    return "\n".join(cleaned_lines)



def remove_references_section(text):
    keywords = {
        "reference", "references",
        "refrence", "refrences",
        "bibliography", "bibliographic",
        "tableofreferences", "listofreferences",
        "referencescited", "referencesbibliography",
        "refernece", "referencelist", "literature", 
        "literaturecited", "workscited", "referencesandnotes",
        "referencesandbibliography", "bibliographyandreferences",
        "referencesandlinks"
    }

    lines = text.splitlines()

    # Search from bottom up to find the start of references
    for i in range(len(lines) - 1, -1, -1):
        cleaned = re.sub(r'[^a-zA-Z]', '', lines[i]).lower()
        if cleaned in keywords:
            return "\n".join(lines[:i])
    
    for i in range(len(lines) - 1, -1, -1):
        if re.match(r'^\s*\[\d+\]', lines[i]):  # e.g. [1], [2], etc.
            return "\n".join(lines[:i])

    for i in range(len(lines) - 1, -1, -1):
        if "address:" in lines[i].lower():
            return "\n".join(lines[:i])

    # If no references section is found, return original text
    return text



def join_lines(text):
    """
    Joins lines in the input text while handling line breaks caused by hyphens at the end of lines.
    """
    lines = text.split("\n")
    processed_lines = []
     
    for i in range(len(lines)):
        if i > 0 and processed_lines and processed_lines[-1].endswith("-"):
            # Merge with the previous line, removing the hyphen
            processed_lines[-1] = processed_lines[-1][:-1] + lines[i].lstrip()
        else:
            processed_lines.append(lines[i])

    return "\n".join(processed_lines)


def remove_short_lines(text, min_words=4):
    """
    Removes lines that contain 3 or fewer words.
    """
    lines = text.split("\n")
    return "\n".join([line for line in lines if len(line.split()) >= min_words])


def remove_lines_with_numbers(text):
    """
    Removes lines that contain only numbers, spaces, or symbols.
    """
    lines = text.split("\n")
    return "\n".join([
        line for line in lines if not re.fullmatch(r"[0-9. \s\(\)-]+", line)
    ])


def clean_text(text):
    """
    Cleans the text by applying multiple text transformations, such as whitespace cleanup, punctuation handling, and unwanted character removal.
    """
    # Remove short words
    text = clean_short_words(text)
    
    # Remove lines with only numbers or symbols
    text = remove_lines_with_numbers(text)
    
    # Remove Remove unnecessary parentheses
    text = re.sub(r'\([^b-z]*\)', '', text)
    
    # Remove extra spaces (but preserve newlines)
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove multiple periods
    text = re.sub(r'\.[.\s]*\.', '.', text)

    # Re-join punctuation
    text = text.replace('( ', '(').replace(' )', ')').replace(' .', '.')

    #  Remove '-' at the beginning or end of words
    text = re.sub(r'-+\s', ' ', text)
    text = re.sub(r'\s-+', ' ', text)

    return text


def preprocessing(text, remove_references):
    """
    Main preprocessing function that applies various cleaning steps to the input text.
    """

    text = text.lower()

    if remove_references:
        text = remove_references_section(text)
   

    # 3. Join lines that end with '-'
    text = join_lines(text)

    # 4. Split dots and parenthesis
    text = text.replace('- ', '').replace('(', ' ( ').replace(')', ' ) ')
    text = re.sub(r'(?<!\d)\.(?!\d|\s)', ' . ', text)  
    text = re.sub(r'(\w)\.(?=\s)', r'\1 . ', text).replace('e . g .', 'e.g.').replace('i . e .', 'i.e.').replace('al .', 'al.')

    # 5.1. Remove everything except a-z, . ' ( ) : and spaces
    text_without_numbers = re.sub(r'(?<=\d)\.(?=\d)', '', text) 
    text_without_numbers = re.sub(r"[^a-z.\-()' \n]", '', text_without_numbers)

    # 5.2. Remove everything except a-z, 0-9 . ' ( ) : and spaces
    text_with_numbers = re.sub(r"[^a-z0-9.\-()' \n]", '', text)

    # 6. Clean text
    text_without_numbers = clean_text(text_without_numbers)
    text_with_numbers = clean_text(text_with_numbers)


    # 7. Remove lines with less than 3 words
    text_without_numbers_short_sentences_removed = remove_short_lines(text_without_numbers)
    # text_with_numbers_short_sentences_removed = remove_short_lines(text_with_numbers)



    return {
        "w_nums": text_with_numbers,
        "wo_nums": text_without_numbers,
        "wo_nums_wo_short": text_without_numbers_short_sentences_removed
    }


def process_row(row):
    original_text = row['pdf_content']
 
    pre_no_ref_removal = preprocessing(original_text, remove_references=False)

    # Step 2: With removing references
    pre_with_ref_removal = preprocessing(original_text, remove_references=True)

    return pd.Series({
        'text_w_ref_w_nums': pre_no_ref_removal['w_nums'],
        'text_wo_ref_w_nums': pre_with_ref_removal['w_nums'],
        'text_wo_ref_wo_nums': pre_with_ref_removal['wo_nums'],
        'text_wo_ref_wo_nums_wo_short': pre_with_ref_removal['wo_nums_wo_short'],
    })

df = pd.read_parquet("data.parquet")

processed_df = df.join(df.apply(process_row, axis=1))


processed_df.to_parquet("data.processed.parquet", index=False)
print("✅ Finished preprocessing and saved to 'data.processed.parquet'")



