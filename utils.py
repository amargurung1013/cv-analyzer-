import os
from pypdf import PdfReader
import pytesseract

if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(pdf_path):

    try:

        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

        return text

    except Exception as e:
        return f"PDF Extraction Error: {str(e)}"