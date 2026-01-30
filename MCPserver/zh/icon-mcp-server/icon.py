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

def mouse_action_delay():
    time.sleep(0.2)

def type_with_delay(text, interval=0.08):
    pyautogui.typewrite(text, interval=interval)


@mcp.tool()
def add_icon_at_position(ctx: Context, text: str, x: int, y: int, w: int, h: int) -> str:

    """
    在目标位置插入名称为**的图标。

    Parameters:
    - x: 图标的中心位置横坐标
    - y: 图标的中心位置纵坐标
    - text: 要插入的图标名称
    - w: 图标的宽度(单位mm)
    - h: 图标的高度(单位mm)

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """

    valid_icons = ["chatgpt", "correct", "deepseek", "error", "fire", "image", "qwen", "snow", "text", "robot", "light", "gear", "network", "book", "medal"]
    if text not in valid_icons:
        return f"错误：无效的图标名称。可用图标名称为：{', '.join(valid_icons)}"
    
    try:
        ori_icon_position = (1100, 850)
        icon_insert = (200, 70)      
        begin_button = (115, 70)      
        width_point = (350, 1260)     
        height_point = (350, 1295)    

        time.sleep(1)
        
        pyautogui.moveTo(icon_insert)
        mouse_action_delay()
        pyautogui.click()

        pyautogui.moveRel(-75, 85)     
        mouse_action_delay()
        pyautogui.click()
        
        pyautogui.moveRel(40, 70)     
        pyautogui.click()
        mouse_action_delay() 
        

        pyautogui.click()
        time.sleep(0.5)
        
        icon_path = f"G:\MCP\MCP-visio\icons\{text}.png"
        for char in icon_path:
            pyautogui.typewrite(char)
            time.sleep(0.01)
        
        mouse_action_delay()
        pyautogui.press('enter')
        mouse_action_delay()
        
        pyautogui.moveTo(ori_icon_position)
        mouse_action_delay()
        pyautogui.mouseDown()
        mouse_action_delay()
        pyautogui.moveTo(x, y)
        mouse_action_delay()
        pyautogui.mouseUp()
        mouse_action_delay()
        
        pyautogui.moveTo(width_point)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()
        
        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.02)

        pyautogui.typewrite(str(w))
        mouse_action_delay()

        pyautogui.moveTo(height_point)
        mouse_action_delay()
        pyautogui.click()
        mouse_action_delay()

        for _ in range(10):
            pyautogui.press('backspace')
            time.sleep(0.02)

        pyautogui.typewrite(str(h))
        mouse_action_delay()
        pyautogui.press('enter')

        pyautogui.moveTo(begin_button)
        mouse_action_delay()
        pyautogui.click()
        
        return f"图标 {text} 已成功添加到坐标({x}, {y})，大小为 {w}x{h}"
    except Exception as e:
        return f"添加图标失败: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
