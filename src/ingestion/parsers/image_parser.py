import pytesseract
from PIL import Image, ImageOps
from pathlib import Path
from typing import List
from src.ingestion.schemas import DocumentElement

class ImageParser:
    """
    Vision Worker responsible for extracting text from images (OCR).
    Handles JPEG and PNG formats.
    """
    def parse(self, path: Path) -> List[DocumentElement]:
        try:
            # 1. Load the image using Pillow
            img = Image.open(path)
            image_format = img.format
            
            # 2. Pre-processing for better OCR accuracy
            # Convert to grayscale (L mode) to remove color noise
            img = ImageOps.grayscale(img)
            
            # 3. Perform OCR using Tesseract
            text = pytesseract.image_to_string(img)
            
            if not text.strip():
                print(f"ℹ️ No text found in image: {path.name}")
                return []

            # 4. Wrap in our Unified Schema
            return [
                DocumentElement(
                    element_type="text",
                    content=text.strip(),
                    source_file=path.name,
                    metadata={
                        "method": "tesseract_ocr",
                        "image_size": img.size,
                        "format": image_format
                    }
                )
            ]
            
        except Exception as e:
            print(f"❌ Error parsing image {path.name}: {e}")
            return []