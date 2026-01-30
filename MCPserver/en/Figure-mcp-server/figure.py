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
def draw_rectangle(ctx: Context, x1: int, y1: int, x2: int, y2: int) -> str:
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
    time.sleep(3)
    try:
        pyautogui.press('esc')
        time.sleep(1)
        pyautogui.hotkey('ctrl', '8')
        time.sleep(1)
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        pyautogui.moveTo(x2, y2, duration=0.5)
        pyautogui.mouseUp()
        return "rectangle drawn successfully."
    except Exception as e:
        return f"Failed to draw rectangle: {str(e)}"


@mcp.tool()
def draw_ellipse(ctx: Context, x1: int, y1: int, x2: int, y2: int) -> str:
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
    time.sleep(3)
    try:
        pyautogui.press('esc')
        time.sleep(1)
        pyautogui.hotkey('ctrl', '9')
        time.sleep(1)
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        pyautogui.moveTo(x2, y2, duration=0.5)
        pyautogui.mouseUp()
        return "ellipse drawn successfully."
    except Exception as e:
        return f"Failed to draw ellipse: {str(e)}"
    
@mcp.tool()
def draw_other_close_figure(ctx: Context, coordinates: list) -> str:
    """
    Draw continuous straight lines on the screen based on the given coordinates.

    Parameters:
    - coordinates: A list of tuples representing (x, y) coordinates.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    time.sleep(3)
    try:
        first_coord = coordinates[0]
        coordinates.append(first_coord)

        time.sleep(2)
        pyautogui.press('esc')
        time.sleep(1)
        pyautogui.hotkey('ctrl', '6')
        time.sleep(1)
        
        start_x, start_y = coordinates[0]
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        
        for i in range(1, len(coordinates)):
            end_x, end_y = coordinates[i]
            pyautogui.moveTo(end_x, end_y, duration=1)
            pyautogui.mouseUp()
            
            if i < len(coordinates) - 1:
                pyautogui.mouseDown()
        
        return "Continuous lines drawn successfully."
    except Exception as e:
        return f"Failed to draw continuous lines: {str(e)}"



def mouse_action_delay():
    time.sleep(0.1)


@mcp.tool()
def draw_cube(ctx: Context, x: int, y: int, w: int, h: int) -> str:
    """
    Draw a cube on the screen.

    Parameters:
    - x: X-coordinate of the cube's center position.
    - y: Y-coordinate of the cube's center position.
    - w: Width of the cube.
    - h: Height of the cube.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        time.sleep(3)
        pyautogui.press('esc')
        time.sleep(1)
        cube_point = (35, 1380)      
        width_point = (350, 1260)    
        height_point = (350, 1290)  

        pyautogui.moveTo(cube_point)
        mouse_action_delay()
        pyautogui.mouseDown()
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.mouseUp()
        mouse_action_delay()

        pyautogui.moveTo(width_point)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()
        
        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.05)

        pyautogui.typewrite(str(w))
        mouse_action_delay()

        pyautogui.moveTo(height_point)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()

        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.05)

        pyautogui.typewrite(str(h))
        mouse_action_delay()
        
        return f"Cube successfully drawn at coordinates ({x}, {y}) with width {w} and height {h}"
    except Exception as e:
        return f"Failed to draw cube: {str(e)}"
    
    
@mcp.tool()
def draw_cylinder(ctx: Context, x: int, y: int, w: int, h: int) -> str:
    """
    Draw a cylinder on the screen.

    Parameters:
    - x: X-coordinate of the cylinder's center position.
    - y: Y-coordinate of the cylinder's center position.
    - w: Width of the cylinder.
    - h: Height of the cylinder.

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        time.sleep(3)
        pyautogui.press('esc')
        time.sleep(1)
        cylinder_point = (35, 1060)   
        width_point = (350, 1260)     
        height_point = (350, 1290)     

        pyautogui.moveTo(cylinder_point)
        mouse_action_delay()
        pyautogui.mouseDown()
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.mouseUp()
        mouse_action_delay()

        pyautogui.moveTo(width_point)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()

        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.05)

        pyautogui.typewrite(str(w))
        mouse_action_delay()

        pyautogui.moveTo(height_point)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()

        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.05)

        pyautogui.typewrite(str(h))
        mouse_action_delay()
        
        return f"Cylinder successfully drawn at coordinates ({x}, {y}) with width {w} and height {h}"
    except Exception as e:
        return f"Failed to draw cylinder: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')