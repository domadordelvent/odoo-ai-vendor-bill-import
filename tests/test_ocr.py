from pdf2image import convert_from_path

pdf_path = "sample.pdf"

pages = convert_from_path(pdf_path)

print(f"Pages: {len(pages)}")

pages[0].save("page1.png", "PNG")

print("First page exported.")
