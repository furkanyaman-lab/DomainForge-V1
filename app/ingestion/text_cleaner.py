
import re

def clean_text(text: str, filename: str) -> str:
    """Remove common PDF extraction noise."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)  
    text = re.sub(r"[ \t]+", " ", text)  
    text = re.sub(r"\n{3,}", "\n\n", text)

    match filename:

        case "Recommendation on the Ethics of Artificial Intelligence.pdf":
            text = re.sub(r"SHS/BIO/REC-AI/2021/1|Recommendation on the Ethics of Artificial Intelligence", "", text, flags=re.IGNORECASE)
            text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

        case "NIST.AI.100-1.pdf":
            text = re.sub(r"NIST\s+AI\s+100-1\s+AI\s+RMF\s+1\.0", "", text, flags=re.IGNORECASE)
            text = re.sub(r"NIST\s+AI\s+100-1", "", text, flags=re.IGNORECASE)
            text = re.sub(r"Page\s+(?:[ivxlcdm]+|\d+)", "", text, flags=re.IGNORECASE)
            text = re.sub(r"^\s*\d+\s+See\s+also\s+http.*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
            text = re.sub(r"(\w+)\.?\d+(\s+)", r"\1\2", text)
            text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

        case "NIST.AI.600-1.pdf":
            text = re.sub(r"Artificial Intelligence Risk Management Framework|Generative Artificial Intelligence Profile|NIST AI \d+-\d+", "", text, flags=re.IGNORECASE)
            text = re.sub(r"^\s*\d+\s+(?:Some|What|The|These|One|See)\s+.*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
            text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"•\s*\n\s*", "• ", text)

        case "OECD AI Principles - Raw - Clairk.pdf":
            text = re.sub(r"OECD Principles on Artificial Intelligence|OECD AI Principles", "", text, flags=re.IGNORECASE)
            text = re.sub(r"[\U000f0000-\U000fFFFF]", "", text)
            text = re.sub(r"Explore|Plain\s+Text", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\d+\s+May\s+\d{4}\s+version|\bAs\s+amended\s+on\s+\d+\s+May\s+\d{4}", "", text, flags=re.IGNORECASE)
            text = re.sub(r"‒\s*", "• ", text)
            
        case _:
            print(f"No specific rule was found for '{filename}', general cleaning applied. ")

    return text.strip()

def clean_documents(documents: list) -> list:
    """Iterates through a list of Document objects and cleans their text in-place.""" 
    for doc in documents:
        doc.text = clean_text(doc.text, doc.source)
    return documents
