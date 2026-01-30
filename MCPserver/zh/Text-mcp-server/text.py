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
    ***注意：***这个模块只能是：矩形，圆形，立方体，圆柱体。
    ***任何其他闭合图形都不适用！！！***
    在绘制好的模块中几何中心输入文字，格式为：- **文本内容:** "----" ，这个信息通常和模块的其他信息一起输出。

    Parameters:
    - text: 要输入的文本内容

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    try:
        # 按下ctrl+2
        pyautogui.hotkey('ctrl', '2')
        time.sleep(1)
        # 模拟键盘输入文本内容，添加间隔
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(0.05)
        # 间隔0.2秒点击回车
        time.sleep(0.2)
        pyautogui.press('esc')
        # 按下ctrl+1
        time.sleep(1)
        pyautogui.hotkey('ctrl', '1')
        return "操作成功完成"
    except Exception as e:
        return f"操作失败: {str(e)}"




@mcp.tool()
def write_text_at_position(ctx: Context, x: int, y: int, w: int, h: int, text: str) -> str:
    """
    在目标位置输入文字，有填充色块，空白位置，任意闭合图形，线条周边位置。

    Parameters:
    - x: 鼠标移动到的目标横坐标
    - y: 鼠标移动到的目标纵坐标
    - w: 文本框宽度
    - h: 文本框高度
    - text: 要输入的文本内容

    Returns:
    - A message indicating the operation result, or an error message if the operation fails.
    """
    none_fill = (2145, 440)   # 无填充按钮位置
    none_line = (2145, 750)  # 无线条按钮位置

    try:
        pyautogui.press('esc')
        time.sleep(0.5)
        # 原操作：移动鼠标到指定坐标并点击左键
        pyautogui.moveTo(x-w/2, y-h/2)
        time.sleep(0.5)

        # 新增操作：按下ctrl+8
        pyautogui.hotkey('ctrl', '8')
        time.sleep(0.5)
        
        # 新增操作：按下鼠标并向右下方移动
        pyautogui.mouseDown()
        pyautogui.moveRel(w, h, duration=0.5)
        pyautogui.mouseUp()
        time.sleep(0.5)
        
        # 新增操作：点击"无填充"和"无线条"
        pyautogui.moveTo(none_line)
        pyautogui.click()
        time.sleep(0.5)
        
        pyautogui.moveTo(none_fill)
        pyautogui.click()
        time.sleep(0.5)
        
        # 模拟键盘输入文本内容，添加间隔
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(0.05)
            
        # 间隔0.2秒按下ctrl+1
        time.sleep(0.2)
        pyautogui.press('esc')
        time.sleep(1)
        pyautogui.hotkey('ctrl', '1')
        
        return "操作成功完成"
    except Exception as e:
        return f"操作失败: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
