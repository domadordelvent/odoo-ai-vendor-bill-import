from PIL import Image
import pytesseract

IMAGE_PATH = "tests/factura1.jpg"

text = pytesseract.image_to_string(
    Image.open(IMAGE_PATH),
    lang="spa"
)

print(text)