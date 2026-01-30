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
def write_text_in_figure(ctx: Context, text: str) -> str:
    """
    ***Note:*** This module is only applicable to: Rectangles, Circles, Cubes, and Cylinders.
    ***It is NOT applicable to any other closed shapes!!!***
    Inputs text at the geometric center of a drawn module. 
    Format: - **Text Content:** "----". This information is usually output along with other module details.

    Parameters:
    - text: The text content to be entered.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        # Press ctrl+2
        pyautogui.hotkey('ctrl', '2')
        time.sleep(1)
        # Simulate keyboard input with intervals
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(0.05)
        # Wait 0.2 seconds then press escape
        time.sleep(0.2)
        pyautogui.press('esc')
        # Press ctrl+1
        time.sleep(1)
        pyautogui.hotkey('ctrl', '1')
        return "Operation completed successfully"
    except Exception as e:
        return f"Operation failed: {str(e)}"




@mcp.tool()
def write_text_at_position(ctx: Context, x: int, y: int, w: int, h: int, text: str) -> str:
    """
    Inputs text at a target position, suitable for filled blocks, empty spaces, 
    arbitrary closed shapes, or positions near lines.

    Parameters:
    - x: Target X-coordinate for the mouse movement
    - y: Target Y-coordinate for the mouse movement
    - w: Width of the text box
    - h: Height of the text box
    - text: The text content to be entered

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    none_fill = (2145, 440)   # Position of the 'No Fill' button
    none_line = (2145, 750)  # Position of the 'No Line' button

    try:
        pyautogui.press('esc')
        time.sleep(0.5)
        # Original operation: move mouse to coordinates and click (calculated from center)
        pyautogui.moveTo(x-w/2, y-h/2)
        time.sleep(0.5)

        # Press ctrl+8
        pyautogui.hotkey('ctrl', '8')
        time.sleep(0.5)
        
        # Mouse down and drag relative to width and height
        pyautogui.mouseDown()
        pyautogui.moveRel(w, h, duration=0.5)
        pyautogui.mouseUp()
        time.sleep(0.5)
        
        # Click "No Line" and "No Fill"
        pyautogui.moveTo(none_line)
        pyautogui.click()
        time.sleep(0.5)
        
        pyautogui.moveTo(none_fill)
        pyautogui.click()
        time.sleep(0.5)
        
        # Simulate keyboard input with intervals
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(0.05)
            
        # Wait 0.2s, press escape, wait 1s, then ctrl+1
        time.sleep(0.2)
        pyautogui.press('esc')
        time.sleep(1)
        pyautogui.hotkey('ctrl', '1')
        
        return "Operation completed successfully"
    except Exception as e:
        return f"Operation failed: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')