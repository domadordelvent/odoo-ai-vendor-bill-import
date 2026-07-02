import fitz
from pdf2image import convert_from_path
import pytesseract


PDF_PATH = "tests/sample.pdf"


def extract_with_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text.strip()


def extract_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""

    for image in images:
        text += pytesseract.image_to_string(image, lang="spa") + "\n"

    return text.strip()


text = extract_with_pymupdf(PDF_PATH)

if text:
    print("PDF amb text detectat. PyMuPDF:")
    print(text)
else:
    print("PDF escanejat detectat. OCR:")
    text = extract_with_ocr(PDF_PATH)
    print(text)