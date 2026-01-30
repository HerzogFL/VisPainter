import pyautogui
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import base64
import io
import os
import tempfile
from typing import Optional, Tuple
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
def make_line_and_fill_figure_settings(ctx: Context, inputs: dict) -> str:
    """
    Sets the fill color block or line format. Supports single color fill only.

    This function accepts English descriptions for input keys. The input should be a dictionary 
    where keys represent different operation points (e.g., "Fill Color", "Corner Radius"), 
    and values are the corresponding input values (e.g., color hex codes, dimensions).

    *** Example input for fill settings ***:
    "Fill Type": "Solid Fill"
    "Fill Color": "#FFD700"
    "Fill Transparency": "--"
    "Line Type": "Solid Line"
    "Solid Line Color": "#FFD700"
    "Solid Line Transparency": "--"
    "Line Width": "--"
    "Line Rounding": "--mm"

    *** Example input for line settings ***:
    "Line Type": "Solid Line"
    "Solid Line Color": "#FFD700"
    "Solid Line Transparency": "--"
    "Line Width": "--"
    "Line Rounding": "--mm"
    "Arrow Type": "Arrow"

    Note: "No Fill", "Solid Fill", "No Line", "Solid Line" are click operations and do not 
    require specific parameter values.
    "Fill Color", "Transparency", "Width", "Rounding", "Arrow" are input operations 
    requiring specific parameters (e.g., {"Solid Line Color": "#C8C8C8"}).
    Rounding inputs must include units (mm), e.g.: "12mm".

    Parameters:
    - inputs: Dictionary containing values for specific points.

    Returns:
    - Success message or error message if the operation fails.
    """

    point_mapping = {
        "Solid Fill": (2150, 470),
        "Fill Color": (2470, 600),
        "Fill Transparency": (2470, 650),
        "Solid Line": (2150, 785),
        "Solid Line Color": (2470, 875),
        "Solid Line Transparency": (2470, 925),
        "Line Width": (2470, 965),
        "Line Rounding": (2470, 1200),
        "Is Arrow": (2470, 1335),
        "Arrow": (2470, 1335),
        "Arrow 2": (2470, 1140),
        "Color 1": (1190, 550),
        "Color 2": (1280, 960),
    }
    order = ["Solid Fill", "Solid Line", "Fill Color", "Fill Transparency", "Solid Line Color", "Solid Line Transparency", "Line Width", "Line Rounding", "Is Arrow"]

    special_operations = []
    for key in ["Fill Type", "Line Type"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:
                special_operations.append(value)

    valid_operations = special_operations + [
        op for op in order 
        if op in inputs or op + " Size" in inputs 
        and op not in special_operations
    ]

    special_operations_2 = []
    for key in ["Is Arrow"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:
                special_operations_2.append(value)
    
    valid_operations = valid_operations + special_operations_2

    try:
        for point_name in valid_operations:
            if point_name in point_mapping:
                x, y = point_mapping[point_name]
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(1)

                if point_name in ["Solid Fill", "Solid Line"]:
                    pyautogui.click()
                elif point_name in ["Fill Transparency", "Solid Line Transparency", "Line Width", "Line Rounding"]:
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, inputs.get(point_name + " Size", ""))
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    pyautogui.press('esc')
                elif point_name in ["Fill Color"]:
                    pyautogui.click()
                    pyautogui.moveRel(0, 650, duration=0.3)
                    pyautogui.click()
                    x_color1, y_color1 = point_mapping["Color 1"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    x_color2, y_color2 = point_mapping["Color 2"]
                    pyautogui.moveTo(x_color2, y_color2, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                elif point_name in ["Solid Line Color"]:
                    pyautogui.click()
                    pyautogui.moveRel(0, 540, duration=0.3)
                    pyautogui.click()
                    x_color1, y_color1 = point_mapping["Color 1"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    x_color2, y_color2 = point_mapping["Color 2"]
                    pyautogui.moveTo(x_color2, y_color2, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                elif point_name in ["Arrow"]:
                    pyautogui.click()
                    x_arrow2, y_arrow2 = point_mapping["Arrow 2"]
                    pyautogui.moveTo(x_arrow2, y_arrow2, duration=0.3)
                    pyautogui.click()
            else:
                return f"Point {point_name} not found in the mapping."
        return "Mouse operations completed successfully."
    except Exception as e:
        return f"Failed to perform mouse operations: {str(e)}"
    


@mcp.tool()
def make_no_fill_figure_settings(ctx: Context, inputs: dict) -> str:
    """
    Sets format for color blocks with no fill. Supports single color line only.
    """

    point_mapping = {
        "No Fill": (2150, 435),
        "Solid Line": (2150, 680),
        "Solid Line Color": (2470, 770),
        "Solid Line Transparency": (2470, 820),
        "Line Width": (2470, 860),
        "Line Rounding": (2470, 1100),
        "Color 1": (1190, 550),
        "Color 2": (1280, 960),
    }
    order = ["No Fill", "Solid Line", "Solid Line Color", "Solid Line Transparency", "Line Width", "Line Rounding"]

    special_operations = []
    for key in ["Fill Type", "Line Type"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:
                special_operations.append(value)

    valid_operations = special_operations + [
        op for op in order 
        if op in inputs or op + " Size" in inputs 
        and op not in special_operations
    ]

    try:
        for point_name in valid_operations:
            if point_name in point_mapping:
                x, y = point_mapping[point_name]
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(0.5)

                if point_name in ["No Fill", "Solid Line"]:
                    pyautogui.click()
                elif point_name in ["Solid Line Transparency", "Line Width", "Line Rounding"]:
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, inputs.get(point_name + " Size", ""))
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    pyautogui.press('esc')
                elif point_name in ["Solid Line Color"]:
                    pyautogui.click()
                    pyautogui.moveRel(0, 540, duration=0.3)
                    pyautogui.click()
                    x_color1, y_color1 = point_mapping["Color 1"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    x_color2, y_color2 = point_mapping["Color 2"]
                    pyautogui.moveTo(x_color2, y_color2, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')
            else:
                return f"Point {point_name} not found in the mapping."
        return "Mouse operations completed successfully."
    except Exception as e:
        return f"Failed to perform mouse operations: {str(e)}"


@mcp.tool()
def make_text_settings(ctx: Context, inputs: dict) -> str:
    """
    Sets text format.

    Supported keys: "Font Selection", "Font Size", "Font Color", "Italic", "Bold".
    Example: {"Font Selection": "Comic Sans MS", "Italic": "Italic", "Bold": "Bold"}
    """

    point_mapping = {
        "Font Selection": (330, 130),
        "Font Size": (415, 130),
        "Font Color": (430, 175),
        "Font Color 1": (1190, 550),
        "Font Color 2": (1280, 960),
        "Italic": (240, 175),
        "Bold": (205, 175),
    }
    order = ["Font Selection", "Font Size", "Font Color", "Italic", "Bold"]

    valid_operations = [op for op in order if op in inputs or op + " Size" in inputs]

    special_operations = []
    for key in ["Italic", "Bold"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:
                special_operations.append(value)

    valid_operations = valid_operations + special_operations

    try:
        for point_name in valid_operations:
            if point_name in point_mapping:
                x, y = point_mapping[point_name]
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(1)

                if point_name in ["Font Selection", "Font Size"]:
                    target_point = point_mapping[point_name]
                    pyautogui.moveTo(target_point[0], target_point[1], duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')

                elif point_name == "Font Color":
                    target_point = point_mapping["Font Color"]
                    pyautogui.moveTo(target_point[0], target_point[1], duration=0.3)
                    pyautogui.click()
                    pyautogui.moveRel(0, 570, duration=0.3)
                    pyautogui.click()
                    x_c1, y_c1 = point_mapping["Font Color 1"]
                    pyautogui.moveTo(x_c1, y_c1, duration=0.3)
                    pyautogui.click()
                    x_c2, y_c2 = point_mapping["Font Color 2"]
                    pyautogui.moveTo(x_c2, y_c2, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')

                elif point_name == "Italic":
                    italic_value = inputs.get(point_name, "")
                    if italic_value == "Italic":
                        x_italic, y_italic = point_mapping["Italic"]
                        pyautogui.moveTo(x_italic, y_italic, duration=0.3)
                        pyautogui.click()

                elif point_name == "Bold":
                    bold_value = inputs.get(point_name, "")
                    if bold_value == "Bold":
                        x_bold, y_bold = point_mapping["Bold"]
                        pyautogui.moveTo(x_bold, y_bold, duration=0.3)
                        pyautogui.click()
            else:
                return f"Point {point_name} not found in the mapping."
            
        time.sleep(0.5)  
        pyautogui.press('esc')
        return "Format settings completed and exited edit mode."
    except Exception as e:
        return f"Failed to perform mouse operations: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')