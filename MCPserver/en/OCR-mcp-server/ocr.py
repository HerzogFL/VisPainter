from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Optional
import pytesseract
from PIL import Image

from mcp.server.fastmcp import Context, FastMCP

# Path configuration for Tesseract OCR engine
pytesseract.pytesseract.tesseract_cmd = r"H:\\pytesseractOCR\\tesseract.exe" 
tessdata_dir_config = '--tessdata-dir H:\\pytesseractOCR\\tessdata'

@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    # Operations at startup
    print("Starting OCR service...")
    try:
        yield
    finally:
        # Operations at shutdown
        print("Shutting down OCR service...")


mcp = FastMCP("OCRService", dependencies=["pytesseract", "Pillow"], lifespan=lifespan, log_level='ERROR')


@mcp.tool()
def find_text_in_image(ctx: Context, image_path: str, text: str) -> str:
    """
    Find the pixel position of specific text within an image.

    Parameters:
    - image_path: Path to the image file.
    - text: The text to search for within the image.

    Returns:
    - A description of the operation result.
    """
    try:
        image = Image.open(image_path)
        # Using 'chi_sim' as in original logic for character data extraction
        data = pytesseract.image_to_boxes(image, lang='chi_sim', config=tessdata_dir_config, output_type=pytesseract.Output.DICT)
        
        all_text = ''.join(data['char'])
        index = all_text.find(text)
        
        if index == -1:
            return f"Text '{text}' was not found in the image."
            
        start_index = index
        end_index = index + len(text) - 1
        
        # Calculate bounding box (handling Tesseract's bottom-up coordinate system)
        left = min([data['left'][i] for i in range(start_index, end_index + 1)])
        top = min([image.height - data['top'][i] for i in range(start_index, end_index + 1)])
        right = max([data['right'][i] for i in range(start_index, end_index + 1)])
        bottom = max([image.height - data['bottom'][i] for i in range(start_index, end_index + 1)])

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        return f"The center pixel position of text '{text}' is: x={center_x}, y={center_y}"
    except Exception as e:
        return f"Text recognition failed: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')