from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Optional
import pytesseract
from PIL import Image

from mcp.server.fastmcp import Context, FastMCP

pytesseract.pytesseract.tesseract_cmd = r"H:\\pytesseractOCR\\tesseract.exe" 
tessdata_dir_config = '--tessdata-dir H:\\pytesseractOCR\\tessdata'

@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    print("Starting OCR service...")
    try:
        yield
    finally:
        print("Shutting down OCR service...")


mcp = FastMCP("OCRService", dependencies=["pytesseract", "Pillow"], lifespan=lifespan, log_level='ERROR')


@mcp.tool()
def find_text_in_image(ctx: Context, image_path: str, text: str) -> str:
    """
    查找图片中特定文本的像素位置。

    参数:
    - image_path: 图片文件的路径。
    - text: 要在图片中查找的文本。

    返回:
    - 操作结果的描述。
    """
    try:
        image = Image.open(image_path)
        data = pytesseract.image_to_boxes(image, lang='chi_sim', config=tessdata_dir_config, output_type=pytesseract.Output.DICT)
        all_text = ''.join(data['char'])
        index = all_text.find(text)
        if index == -1:
            return f"文本 '{text}' 未在图片中找到。"
        start_index = index
        end_index = index + len(text) - 1
        left = min([data['left'][i] for i in range(start_index, end_index + 1)])
        top = min([image.height - data['top'][i] for i in range(start_index, end_index + 1)])
        right = max([data['right'][i] for i in range(start_index, end_index + 1)])
        bottom = max([image.height - data['bottom'][i] for i in range(start_index, end_index + 1)])

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        return f"文本 '{text}' 的中心像素位置为: x={center_x}, y={center_y}"
    except Exception as e:
        return f"文本识别失败: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
    