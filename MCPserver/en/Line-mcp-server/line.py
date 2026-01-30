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
def draw_straight_line(ctx: Context, x1: int, y1: int, x2: int, y2: int) -> str:
    """
    Draw a straight line on the screen from (x1, y1) to (x2, y2).

    Parameters:
    - x1: X coordinate of the starting point.
    - y1: Y coordinate of the starting point.
    - x2: X coordinate of the ending point.
    - y2: Y coordinate of the ending point.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        pyautogui.hotkey('ctrl', '6')
        time.sleep(1)
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        pyautogui.moveTo(x2, y2, duration=0.5)
        pyautogui.mouseUp()
        return "Straight line drawn successfully."
    except Exception as e:
        return f"Failed to draw straight line: {str(e)}"


@mcp.tool()
def draw_curve(ctx: Context, coordinates: list) -> str:
    """
    Draw a curve on the screen passing through the given coordinates.

    Parameters:
    - coordinates: A list of tuples representing (x, y) coordinates.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        pyautogui.hotkey('ctrl', '5')
        pyautogui.moveTo(coordinates[0][0], coordinates[0][1])
        pyautogui.mouseDown()
        for x, y in coordinates[1:]:
            pyautogui.moveTo(x, y, duration=1)
        pyautogui.mouseUp()
        return "Curve drawn successfully."
    except Exception as e:
        return f"Failed to draw curve: {str(e)}"


@mcp.tool()
def draw_continuous_lines(ctx: Context, coordinates: list) -> str:
    """
    Draw continuous straight lines on the screen based on the given coordinates.

    Parameters:
    - coordinates: A list of tuples representing (x, y) coordinates.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        time.sleep(5)
        pyautogui.hotkey('ctrl', '6')
        time.sleep(1)
        
        # Move to the first coordinate and press the mouse button
        start_x, start_y = coordinates[0]
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        
        for i in range(1, len(coordinates)):
            end_x, end_y = coordinates[i]
            pyautogui.moveTo(end_x, end_y, duration=1)
            pyautogui.mouseUp()
            
            # Except for the last coordinate, press the mouse button again at the current position after each release
            if i < len(coordinates) - 1:
                pyautogui.mouseDown()
        
        return "Continuous lines drawn successfully."
    except Exception as e:
        return f"Failed to draw continuous lines: {str(e)}"
    


@mcp.tool()
def Initialize_visio_drawing(ctx: Context) -> str:
    """
    Perform custom mouse operations:
    1. Press ctrl + 8.
    2. Move the mouse to the center of the screen.
    3. Right - click the mouse.
    4. Move the mouse 50 pixels to the right and 50 pixels down.
    5. Left - click the mouse.
    6. Move the mouse 50 pixels to the right and 450 pixels down.
    7. Press the Delete key.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        # Press ctrl + 8
        pyautogui.hotkey('ctrl', '8')
        time.sleep(1)

        # Get the screen size
        screen_width, screen_height = pyautogui.size()

        # Move the mouse to the center of the screen
        center_x = screen_width // 2
        center_y = screen_height // 2
        # pyautogui.moveTo(center_x, center_y)
        pyautogui.moveTo(120, 300)
        # Right - click the mouse
        pyautogui.mouseDown()
        time.sleep(1)

        # Move the mouse 50 pixels to the right and 50 pixels down
        pyautogui.moveRel(50, 50)
        pyautogui.mouseUp()

        # Left - click the mouse
        pyautogui.rightClick()
        time.sleep(1)

        # Move the mouse 50 pixels to the right and 450 pixels down
        pyautogui.moveRel(50, 400)
        pyautogui.leftClick()

        time.sleep(1)
        pyautogui.moveTo(2125, 435,duration=1)
        pyautogui.leftClick()

        time.sleep(1)
        pyautogui.moveTo(2125, 390, duration=1)
        pyautogui.leftClick()


        pyautogui.press('delete')

        return "Custom mouse operations completed successfully."
    except Exception as e:
        return f"Failed to perform custom mouse operations: {str(e)}"



if __name__ == "__main__":
    mcp.run(transport='stdio')