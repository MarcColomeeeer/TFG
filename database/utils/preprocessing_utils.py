import re 
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

def join_lines(text):
    """
    Joins lines in the input text while handling line breaks caused by hyphens at the end of lines.
    """
    lines = text.split("\n")
    processed_lines = []
     
    for i in range(len(lines)):
        if i > 0 and processed_lines and processed_lines[-1].endswith("-"):
            processed_lines[-1] = processed_lines[-1][:-1] + lines[i].lstrip()
        else:
            processed_lines.append(lines[i])

    return "\n".join(processed_lines)


def count_token_frequencies(tokens):
    """
    Counts token frequencies and returns a dictionary (manual count, no Counter).
    """
    freq_dict = {}
    for token in tokens:
        freq_dict[token] = freq_dict.get(token, 0) + 1
    return freq_dict


def extract_token_frequencies(text):
    """
    Main preprocessing function that applies various cleaning steps to the input text.
    """
    text = text.lower()
    text = join_lines(text)
    text = re.sub(r"[^a-z \n]", '', text)

    tokens = text.split()
    tokens = [word for word in tokens if len(word) > 2]

    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    return count_token_frequencies(tokens)