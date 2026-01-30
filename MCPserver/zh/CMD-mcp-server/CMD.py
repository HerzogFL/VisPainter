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
    根据坐标选中模块并修改宽高

    Parameters:
    - source_x: 目标模块的X坐标
    - source_y: 目标模块的Y坐标
    - target_w: 目标宽度（毫米值，一毫米等效5像素）
    - target_h: 目标高度（毫米值，一毫米等效5像素）

    Returns:
    - 操作结果信息，失败时返回错误信息
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

        return f"模块尺寸修改成功：宽度={target_w}px，高度={target_h}px"

    except Exception as e:
        return f"尺寸修改失败: {str(e)}"



@mcp.tool()
def copy_module_to_position(source_x: int, source_y: int, area_x: int, area_y: int, target_x: int, target_y: int) -> str:
    """
    将模块从源位置复制到目标位置

    Parameters:
    - source_x: 源位置的X坐标
    - source_y: 源位置的Y坐标
    - area_x: 被操作区域的宽度
    - area_y: 被操作区域的高度
    - target_x: 目标位置的X坐标
    - target_y: 目标位置的Y坐标

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

        return f"模块从坐标({source_x}, {source_y})成功复制到坐标({target_x}, {target_y})"
    except Exception as e:
        return f"复制操作失败: {str(e)}"


@mcp.tool()
def move_module_to_position(source_x: int, source_y: int, area_x: int, area_y: int, target_x: int, target_y: int) -> str:
    """
    将模块从源位置移动到目标位置

    Parameters:
    - source_x: 源位置的X坐标
    - source_y: 源位置的Y坐标
    - area_x: 被操作区域的宽度
    - area_y: 被操作区域的高度
    - target_x: 目标位置的X坐标
    - target_y: 目标位置的Y坐标

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        # 移动到源位置并剪切
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

        return f"模块从坐标({source_x}, {source_y})成功移动到坐标({target_x}, {target_y})"
    except Exception as e:
        return f"移动操作失败: {str(e)}"


@mcp.tool()
def delete_module_at_position(x: int, y: int, area_x: int, area_y: int,) -> str:
    """
    删除指定位置的模块

    Parameters:
    - x: 模块位置的X坐标
    - y: 模块位置的Y坐标
    - area_x: 被操作区域的宽度
    - area_y: 被操作区域的高度

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

        return f"坐标({x}, {y})处的模块已成功删除"
    except Exception as e:
        return f"删除操作失败: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')