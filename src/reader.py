import os
from pypdf import PdfReader

def read_text_file(file_path: str) -> str:
    """
    Reads content from a text file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf_file(file_path: str) -> str:
    """
    Extracts text from a PDF file.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        raise e
    return text

def read_file(file_path: str) -> str:
    """
    Detects file type by extension and returns extracted text.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.txt':
        return read_text_file(file_path)
    elif ext == '.pdf':
        return read_pdf_file(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

