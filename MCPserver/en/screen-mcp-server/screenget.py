# Add lifespan support for startup/shutdown with strong typing
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import base64
import io
import os
import tempfile
from typing import Optional, Tuple
import pyautogui
import time
import zipfile
from cryptography.fernet import Fernet
from PIL import Image

from mcp.server.fastmcp import Context, FastMCP

# Add lifecycle management for the application
@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    # Operations at startup
    print("Starting LocalPlay service...")
    # Initialize resources, connect to database, etc. here

    try:
        yield  # During service operation
    finally:
        # Operations at shutdown
        print("Shutting down LocalPlay service...")
        # Clean up resources, close connections, etc. here

# Specify dependencies for deployment and development
mcp = FastMCP("LocalPlay", dependencies=["pyautogui", "cryptography", "Pillow"], lifespan=lifespan, log_level='ERROR')

# Generate encryption key
key = Fernet.generate_key()
cipher_suite = Fernet(key)


@mcp.tool()
def get_single_screen_screenshot(ctx: Context, x: Optional[int] = None, y: Optional[int] = None,
                                 width: Optional[int] = None, height: Optional[int] = None,
                                 save_path: str = None, file_format: str = 'png',
                                 encrypt: bool = False, compress: bool = False) -> str:
    """
    Capture a single screenshot of the screen or a specified region.

    Parameters:
    - x: Optional, X coordinate of the top-left corner of the region to capture.
         If not provided, the entire screen will be captured.
    - y: Optional, Y coordinate of the top-left corner of the region to capture.
         If not provided, the entire screen will be captured.
    - width: Optional, Width of the region to capture.
             If not provided along with x and y, the entire screen will be captured.
    - height: Optional, Height of the region to capture.
              If not provided along with x and y, the entire screen will be captured.
    - save_path: Optional, Path to save the screenshot. If not provided, a temporary file will be used.
    - file_format: Optional, File format of the screenshot, options: 'png', 'jpeg', 'bmp', default is 'png'.
    - encrypt: Optional, Whether to encrypt the screenshot, default is False.
    - compress: Optional, Whether to compress the screenshot, default is False.

    Returns:
    - A message indicating the path where the screenshot is saved, or an error message if the operation fails.
    """
    try:
        if x is not None and y is not None and width is not None and height is not None:
            x=200
            y=200
            width=512
            height=512
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()

        if save_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix=f'.{file_format}', delete=False)
            save_path = temp_file.name
        else:
            if not save_path.endswith(f'.{file_format}'):
                save_path = f'{save_path}.{file_format}'

        screenshot.save(save_path)

        if encrypt:
            with open(save_path, 'rb') as f:
                data = f.read()
            encrypted_data = cipher_suite.encrypt(data)
            with open(save_path, 'wb') as f:
                f.write(encrypted_data)

        if compress:
            zip_file_path = f'{os.path.splitext(save_path)[0]}.zip'
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(save_path, os.path.basename(save_path))
            os.remove(save_path)
            save_path = zip_file_path

        return f"Screenshot saved to {save_path}"
    except Exception as e:
        return f"Screenshot capture failed: {str(e)}"

# @mcp.tool()
# def get_periodic_screen_screenshots(ctx: Context, x: Optional[int] = None, y: Optional[int] = None,
#                                     width: Optional[int] = None, height: Optional[int] = None,
#                                     interval: float = 5, num_screenshots: int = -1,
#                                     save_path: str = None, file_format: str = 'png',
#                                     encrypt: bool = False, compress: bool = False,
#                                     naming_rule: str = 'timestamp') -> str:
#     """
#     Periodically capture screenshots of the screen or a specified region.

#     Parameters:
#     - x: Optional, X coordinate of the top-left corner of the region to capture.
#          If not provided, the entire screen will be captured.
#     - y: Optional, Y coordinate of the top-left corner of the region to capture.
#          If not provided, the entire screen will be captured.
#     - width: Optional, Width of the region to capture.
#              If not provided along with x and y, the entire screen will be captured.
#     - height: Optional, Height of the region to capture.
#               If not provided along with x and y, the entire screen will be captured.
#     - interval: Time interval (in seconds) between each screenshot capture, default is 5 seconds.
#     - num_screenshots: Number of screenshots to capture. If set to -1, it will capture screenshots indefinitely.
#     - save_path: Optional, Path to save the screenshots. If not provided, temporary files will be used.
#     - file_format: Optional, File format of the screenshots, options: 'png', 'jpeg', 'bmp', default is 'png'.
#     - encrypt: Optional, Whether to encrypt the screenshots, default is False.
#     - compress: Optional, Whether to compress the screenshots, default is False.
#     - naming_rule: Optional, Naming rule for the screenshots, options: 'timestamp', 'sequential', default is 'timestamp'.

#     Returns:
#     - A message indicating the operation status, or an error message if the operation fails.
#     """
#     try:
#         count = 0
#         if num_screenshots == -1:
#             print(f"Starting to capture screenshots every {interval} seconds indefinitely.")
#         else:
#             print(f"Starting to capture {num_screenshots} screenshots every {interval} seconds.")

#         while num_screenshots == -1 or count < num_screenshots:
#             if x is not None and y is not None and width is not None and height is not None:
#                 x=200
#                 y=200
#                 width=512
#                 height=512
#                 screenshot = pyautogui.screenshot(region=(x, y, width, height))
#             else:
#                 screenshot = pyautogui.screenshot()

#             if save_path is None:
#                 temp_file = tempfile.NamedTemporaryFile(suffix=f'.{file_format}', delete=False)
#                 current_save_path = temp_file.name
#             else:
#                 if naming_rule == 'timestamp':
#                     timestamp = time.strftime("%Y%m%d-%H%M%S")
#                     current_save_path = os.path.join(save_path, f'screenshot_{timestamp}.{file_format}')
#                 elif naming_rule == 'sequential':
#                     current_save_path = os.path.join(save_path, f'screenshot_{count + 1}.{file_format}')
#                 else:
#                     raise ValueError(f"Invalid naming rule: {naming_rule}")

#             screenshot.save(current_save_path)

#             if encrypt:
#                 with open(current_save_path, 'rb') as f:
#                     data = f.read()
#                 encrypted_data = cipher_suite.encrypt(data)
#                 with open(current_save_path, 'wb') as f:
#                     f.write(encrypted_data)

#             if compress:
#                 zip_file_path = f'{os.path.splitext(current_save_path)[0]}.zip'
#                 with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
#                     zipf.write(current_save_path, os.path.basename(current_save_path))
#                 os.remove(current_save_path)
#                 current_save_path = zip_file_path

#             print(f"Screenshot saved to {current_save_path}")
#             count += 1
#             time.sleep(interval)

#         if num_screenshots != -1:
#             return f"Successfully captured {num_screenshots} screenshots as scheduled."
#         else:
#             return "Continuing to capture screenshots indefinitely."
#     except Exception as e:
#         return f"Scheduled screenshot capture failed: {str(e)}"


@mcp.tool()
def compare_screenshots(ctx: Context, screenshot1_path: str, screenshot2_path: str) -> str:
    """
    Compare two screenshots and find differences.

    Parameters:
    - screenshot1_path: Path to the first screenshot.
    - screenshot2_path: Path to the second screenshot.

    Returns:
    - A message indicating the comparison result, or an error message if the operation fails.
    """
    try:
        img1 = Image.open(screenshot1_path)
        img2 = Image.open(screenshot2_path)

        diff = ImageChops.difference(img1, img2)
        if diff.getbbox() is None:
            return "The two screenshots are identical."
        else:
            return "There are differences between the two screenshots."
    except Exception as e:
        return f"Screenshot comparison failed: {str(e)}"


@mcp.tool()
def save_existing_screenshot(ctx: Context, source_path: str, destination_path: str,
                             file_format: str = 'png', encrypt: bool = False, compress: bool = False) -> str:
    """
    Save an existing screenshot to a new location with optional format conversion, encryption, and compression.

    Parameters:
    - source_path: Path to the existing screenshot.
    - destination_path: Path to save the screenshot.
    - file_format: Optional, File format of the screenshot, options: 'png', 'jpeg', 'bmp', default is 'png'.
    - encrypt: Optional, Whether to encrypt the screenshot, default is False.
    - compress: Optional, Whether to compress the screenshot, default is False.

    Returns:
    - A message indicating the path where the screenshot is saved, or an error message if the operation fails.
    """
    try:
        if not os.path.exists(source_path):
            return f"Source screenshot file {source_path} does not exist."

        if not destination_path.endswith(f'.{file_format}'):
            destination_path = f'{destination_path}.{file_format}'

        img = Image.open(source_path)
        img.save(destination_path)

        if encrypt:
            with open(destination_path, 'rb') as f:
                data = f.read()
            encrypted_data = cipher_suite.encrypt(data)
            with open(destination_path, 'wb') as f:
                f.write(encrypted_data)

        if compress:
            zip_file_path = f'{os.path.splitext(destination_path)[0]}.zip'
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(destination_path, os.path.basename(destination_path))
            os.remove(destination_path)
            destination_path = zip_file_path

        return f"Screenshot saved to {destination_path}"
    except Exception as e:
        return f"Saving screenshot failed: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')