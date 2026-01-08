import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os

# ✅ Explicit paths (NO ADMIN REQUIRED)
TESSERACT_CMD = r"C:\Users\16301\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\poppler-25.12.0\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text(file_path: str) -> str:
    """
    Extract text from PDF or image using OCR.
    Works on corporate laptops (no PATH dependency).
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text = ""

    if file_path.lower().endswith(".pdf"):
        images = convert_from_path(
            file_path,
            poppler_path=POPPLER_PATH
        )
        for img in images:
            text += pytesseract.image_to_string(img)

    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    return text.strip()
