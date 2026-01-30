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

pyautogui.FAILSAFE = False

def mouse_action_delay():
    time.sleep(0.1)

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
def change_module_size_in_position(source_x: int, source_y: int, target_w: int, target_h: int) -> str:
    """
    Select a module based on coordinates and modify its width and height.

    Parameters:
    - source_x: X coordinate of the target module
    - source_y: Y coordinate of the target module
    - target_w: Target width (in millimeters, 1mm is equivalent to 5 pixels)
    - target_h: Target height (in millimeters, 1mm is equivalent to 5 pixels)

    Returns:
    - Information about the operation result, or an error message if it fails.
    """
    try:

        width_point = (350, 1260)   
        height_point = (350, 1290) 


        pyautogui.moveTo(source_x, source_y, duration=0.2)  
        mouse_action_delay()
        pyautogui.click() 
        mouse_action_delay()


        pyautogui.moveTo(width_point[0], width_point[1], duration=0.2)
        mouse_action_delay()
        pyautogui.click()  
        mouse_action_delay()

        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.05)
        mouse_action_delay()

        pyautogui.typewrite(str(target_w))
        mouse_action_delay()

        pyautogui.moveTo(height_point[0], height_point[1], duration=0.2)
        mouse_action_delay()
        pyautogui.click() 
        mouse_action_delay()

        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.05)
        mouse_action_delay()

        pyautogui.typewrite(str(target_h))
        mouse_action_delay()

        pyautogui.press('enter')
        mouse_action_delay()

        return f"Module size modified successfully: width={target_w}px, height={target_h}px"

    except Exception as e:
        return f"Size modification failed: {str(e)}"



@mcp.tool()
def copy_module_to_position(source_x: int, source_y: int, area_x: int, area_y: int, target_x: int, target_y: int) -> str:
    """
    Copy a module from the source position to the target position.

    Parameters:
    - source_x: X coordinate of the source position
    - source_y: Y coordinate of the source position
    - area_x: Width of the selection area
    - area_y: Height of the selection area
    - target_x: X coordinate of the target position
    - target_y: Y coordinate of the target position

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        time.sleep(1)
        pyautogui.hotkey('ctrl', '1')
        pyautogui.moveTo(source_x-area_x/2, source_y-area_y/2)
        mouse_action_delay()
        pyautogui.mouseDown()
        mouse_action_delay()
        pyautogui.moveTo(source_x+area_x/2, source_y+area_y/2)
        mouse_action_delay()
        pyautogui.mouseUp()
        mouse_action_delay()
        pyautogui.hotkey('ctrl', 'c')
        mouse_action_delay()

        pyautogui.moveTo(target_x, target_y)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()
        pyautogui.hotkey('ctrl', 'v')
        mouse_action_delay()

        return f"Module at coordinates ({source_x}, {source_y}) successfully copied to coordinates ({target_x}, {target_y})"
    except Exception as e:
        return f"Copy operation failed: {str(e)}"


@mcp.tool()
def move_module_to_position(source_x: int, source_y: int, area_x: int, area_y: int, target_x: int, target_y: int) -> str:
    """
    Move a module from the source position to the target position.

    Parameters:
    - source_x: X coordinate of the source position
    - source_y: Y coordinate of the source position
    - area_x: Width of the selection area
    - area_y: Height of the selection area
    - target_x: X coordinate of the target position
    - target_y: Y coordinate of the target position

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        # Move to source position and cut
        time.sleep(1)
        pyautogui.hotkey('ctrl', '1')
        pyautogui.moveTo(source_x-area_x/2, source_y-area_y/2)
        mouse_action_delay()
        pyautogui.mouseDown()
        mouse_action_delay()
        pyautogui.moveTo(source_x+area_x/2, source_y+area_y/2)
        mouse_action_delay()
        pyautogui.mouseUp()
        mouse_action_delay()
        pyautogui.hotkey('ctrl', 'x')
        mouse_action_delay()

        pyautogui.moveTo(target_x, target_y)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()
        pyautogui.hotkey('ctrl', 'v')
        mouse_action_delay()

        return f"Module at coordinates ({source_x}, {source_y}) successfully moved to coordinates ({target_x}, {target_y})"
    except Exception as e:
        return f"Move operation failed: {str(e)}"


@mcp.tool()
def delete_module_at_position(x: int, y: int, area_x: int, area_y: int,) -> str:
    """
    Delete the module at the specified position.

    Parameters:
    - x: X coordinate of the module position
    - y: Y coordinate of the module position
    - area_x: Width of the selection area
    - area_y: Height of the selection area

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        time.sleep(1)
        pyautogui.hotkey('ctrl', '1')
        pyautogui.moveTo(x-area_x/2, y-area_y/2)
        mouse_action_delay()
        pyautogui.mouseDown()
        mouse_action_delay()
        pyautogui.moveTo(x+area_x/2, y+area_y/2)
        mouse_action_delay()
        pyautogui.mouseUp()

        pyautogui.press('delete')
        mouse_action_delay()

        return f"Module at coordinates ({x}, {y}) successfully deleted"
    except Exception as e:
        return f"Delete operation failed: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')