from ai.document_extractor import extract_text

files = [
    "tests/factura2.pdf",
    "tests/factura1.jpg",
]

for file in files:
    print("\n" + "=" * 80)
    print(file)
    print("=" * 80)
    print(extract_text(file))