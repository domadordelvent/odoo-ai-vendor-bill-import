from pathlib import Path

import fitz
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_from_pdf(path)

    if suffix in [".jpg", ".jpeg", ".png"]:
        return extract_from_image(path)

    raise ValueError(f"Unsupported file type: {suffix}")


def extract_from_pdf(path: Path) -> str:
    text = extract_pdf_text_with_pymupdf(path)

    if text:
        return text

    return extract_pdf_text_with_ocr(path)


def extract_pdf_text_with_pymupdf(path: Path) -> str:
    doc = fitz.open(path)
    text = ""

    for page in doc:
        text += page.get_text() + "\n"

    return text.strip()


def extract_pdf_text_with_ocr(path: Path) -> str:
    images = convert_from_path(path)
    text = ""

    for image in images:
        text += pytesseract.image_to_string(image, lang="spa") + "\n"

    return text.strip()


def extract_from_image(path: Path) -> str:
    return pytesseract.image_to_string(
        Image.open(path),
        lang="spa"
    ).strip()