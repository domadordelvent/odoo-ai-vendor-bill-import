import fitz  # PyMuPDF


pdf_path = "sample.pdf"

doc = fitz.open(pdf_path)

full_text = ""

for page in doc:
    full_text += page.get_text()

print("Extracted text:")
print("-" * 50)
print(full_text[:2000])