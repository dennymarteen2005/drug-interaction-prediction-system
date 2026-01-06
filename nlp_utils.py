import re

def extract_drugs(text, drug_list):
    """
    Lightweight, EXE-safe drug extraction.
    Matches known drug names from dataset.
    """

    text = text.lower()
    found = set()

    for drug in drug_list:
        pattern = r"\b" + re.escape(drug.lower()) + r"\b"
        if re.search(pattern, text):
            found.add(drug.lower())

    return list(found)
