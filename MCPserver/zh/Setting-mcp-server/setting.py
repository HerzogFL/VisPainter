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
    设置有填充色块或者线条格式，仅支持单色填充！！！。

    本函数仅接受中文描述的输入。输入应为一个字典，其中键表示不同的操作点（例如 “填充颜色”、“圆角大小” 等），值为对应操作的输入值（例如颜色值、尺寸值等）。
    ***这是一条有填充色块设置的输入示例***：
    "是否填充": 纯色填充"
    "填充颜色": #FFD700"
    "填充透明度":--"
    "线条类型":实线"
    "实线颜色":#FFD700"
    "实线透明度":--"
    "线条宽度":--"
    "线条圆角":--mm"
    ***这是一条线条设置的输入示例***：
    "线条类型":实线"
    "实线颜色":#FFD700"
    "实线透明度":--"
    "线条宽度":--"
    "线条圆角":--mm"
    "是否箭头": 箭头"

    其中"无填充"，"纯色填充"，"无线条"，"实线"为点击操作，不需要具体参数输入，例如：{"实线": ""}
    "填充颜色"，"填充透明度"，"实线颜色"，"实线透明度"，"宽度"，"圆角"，"箭头"为输入操作，需要具体参数输入，例如{"实线颜色": "#C8C8C8"}。
    "圆角输入必须含有单位mm，例如：12mm"。

    参数:
    - inputs: 包含特定点输入值的字典（例如颜色、尺寸）。

    返回:
    - 操作结果的消息，如果操作失败则返回错误消息。
    """

    point_mapping = {
        "纯色填充": (2150, 470),
        "填充颜色": (2470, 600),
        "填充透明度": (2470, 650),
        "实线": (2150, 785),
        "实线颜色": (2470, 875),
        "实线透明度": (2470, 925),
        "线条宽度": (2470, 965),
        "线条圆角": (2470, 1200),
        "是否箭头": (2470, 1335),
        "箭头": (2470, 1335),
        "箭头2": (2470, 1140),
        "颜色1": (1190, 550),
        "颜色2": (1280, 960),
    }
    order = ["纯色填充", "实线", "填充颜色", "填充透明度", "实线颜色", "实线透明度", "线条宽度", "线条圆角", "是否箭头"]

    # 直接从输入中提取"是否填充"和"线条类型"的值
    special_operations = []
    for key in ["是否填充", "线条类型"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:  # 确保值对应有效的操作点
                special_operations.append(value)

    # 构建有效操作列表，特殊操作在前
    valid_operations = special_operations + [
        op for op in order 
        if op in inputs or op + "大小" in inputs 
        and op not in special_operations  # 避免重复
    ]

    special_operations_2 = []
    for key in ["是否箭头"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:  # 确保值对应有效的操作点
                special_operations_2.append(value)
    
    valid_operations = valid_operations + special_operations_2

    # # 筛选出输入中存在的操作
    # valid_operations = [op for op in order if op in inputs or op + "大小" in inputs]

    try:
        for point_name in valid_operations:
            if point_name in point_mapping:
                x, y = point_mapping[point_name]
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(1)  # 可以根据需要调整等待时间

                if point_name in [ "纯色填充", "实线"]:
                    pyautogui.click()
                elif point_name in ["填充透明度", "实线透明度", "线条宽度", "线条圆角"]:
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, inputs.get(point_name + "大小", ""))
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 添加延迟以确保每个字符正确输入
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('esc')
                elif point_name in ["填充颜色"]:
                    pyautogui.click()
                    pyautogui.moveRel(0, 650, duration=0.3)
                    pyautogui.click()
                    x_color1, y_color1 = point_mapping["颜色1"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    x_color2, y_color2 = point_mapping["颜色2"]
                    pyautogui.moveTo(x_color2, y_color2, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 增加延迟时间
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('enter')
                elif point_name in ["实线颜色"]:
                    pyautogui.click()
                    pyautogui.moveRel(0, 540, duration=0.3)
                    pyautogui.click()
                    x_color1, y_color1 = point_mapping["颜色1"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    x_color2, y_color2 = point_mapping["颜色2"]
                    pyautogui.moveTo(x_color2, y_color2, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 增加延迟时间
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('enter')
                elif point_name in ["箭头"]:
                    pyautogui.click()
                    x_arrow2, y_arrow2 = point_mapping["箭头2"]
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
    设置无填充色块格式，不支持线条设置，仅支持单色填充！！！。

    本函数仅接受中文描述的输入。输入应为一个字典，其中键表示不同的操作点（例如 “填充颜色”、“圆角大小” 等），值为对应操作的输入值（例如颜色值、尺寸值等）。
    这是一条输入示例：
    "是否填充: 无填充"
    "线条类型:实线"
    "实线颜色:#FFD700"
    "实线透明度:--"
    "线条宽度: --"
    "线条圆角: --mm"
    其中"无填充"，"纯色填充"，"无线条"，"实线"为点击操作，不需要具体参数输入，例如：{"实线": ""}
    "填充颜色"，"填充透明度"，"实线颜色"，"实线透明度"，"宽度"，"圆角"，"箭头"为输入操作，需要具体参数输入，例如{"实线颜色": "#C8C8C8"}。
    "圆角输入必须含有单位mm，例如：12mm"。

    参数:
    - inputs: 包含特定点输入值的字典（例如颜色、尺寸）。

    返回:
    - 操作结果的消息，如果操作失败则返回错误消息。
    """

    point_mapping = {
        "无填充": (2150, 435),
        "实线": (2150, 680),
        "实线颜色": (2470, 770),
        "实线透明度": (2470, 820),
        "线条宽度": (2470, 860),
        "线条圆角": (2470, 1100),
        "颜色1": (1190, 550),
        "颜色2": (1280, 960),
    }
    order = ["无填充","实线", "实线颜色", "实线透明度", "线条宽度", "线条圆角"]


    # 直接从输入中提取"是否填充"和"线条类型"的值
    special_operations = []
    for key in ["是否填充", "线条类型"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:  # 确保值对应有效的操作点
                special_operations.append(value)

    # 构建有效操作列表，特殊操作在前
    valid_operations = special_operations + [
        op for op in order 
        if op in inputs or op + "大小" in inputs 
        and op not in special_operations  # 避免重复
    ]

    # 筛选出输入中存在的操作
    # valid_operations = [op for op in order if op in inputs or op + "大小" in inputs]

    try:
        for point_name in valid_operations:
            if point_name in point_mapping:
                x, y = point_mapping[point_name]
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(0.5)  # 可以根据需要调整等待时间

                if point_name in ["无填充", "实线"]:
                    pyautogui.click()
                elif point_name in ["实线透明度", "线条宽度", "线条圆角"]:
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, inputs.get(point_name + "大小", ""))
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 添加延迟以确保每个字符正确输入
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('esc')
                elif point_name in ["实线颜色"]:
                    pyautogui.click()
                    pyautogui.moveRel(0, 540, duration=0.3)
                    pyautogui.click()
                    x_color1, y_color1 = point_mapping["颜色1"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    x_color2, y_color2 = point_mapping["颜色2"]
                    pyautogui.moveTo(x_color2, y_color2, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 增加延迟时间
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('enter')
            else:
                return f"Point {point_name} not found in the mapping."
        return "Mouse operations completed successfully."
    except Exception as e:
        return f"Failed to perform mouse operations: {str(e)}"


# make_text_settings函数同理修改
@mcp.tool()
def make_text_settings(ctx: Context, inputs: dict) -> str:
    """
    设置文本格式。

    本函数仅接受中文描述的输入。输入应为一个字典，其中键表示不同的操作点（例如 “字体选择”、“字体颜色” 等），值为对应操作的输入值（例如颜色值、尺寸值等）。
    输入的字典只可以包含以下键："字体选择", "字号大小", "字体颜色", "字体斜体", "字体加粗"，这是输入的样例：
    "字体选择": Comic Sans MS"
    "字号大小": --"
    "字体颜色": #FFD700"
    "字体斜体": 非斜体"
    "字体加粗": 加粗"

    其中"字体斜体", "字体加粗"为点击操作，不需要具体参数输入，例如：{"字体斜体": ""}
    "字体选择", "字号大小", "字体颜色"为输入操作，需要具体参数输入，文本类型，例如{"字体颜色": "#C8C8C8"}。

    参数:
    - inputs: 包含特定点输入值的字典（例如颜色、尺寸）。

    返回:
    - 操作结果的消息，如果操作失败则返回错误消息。
    """

    point_mapping = {
        "字体选择": (330, 130),
        "字号大小": (415, 130),
        "字体颜色": (430, 175),
        "字体颜色1": (1190, 550),
        "字体颜色2": (1280, 960),
        "字体斜体": (240, 175),
        "字体加粗": (205, 175),
    }
    order = ["字体选择", "字号大小", "字体颜色", "字体斜体", "字体加粗"]

    # 筛选出输入中存在的操作
    valid_operations = [op for op in order if op in inputs or op + "大小" in inputs]

    # 直接从输入中提取"字体斜体"和"字体加粗"的值
    special_operations = []
    for key in ["字体斜体", "字体加粗"]:
        if key in inputs:
            value = inputs[key]
            if value in point_mapping:  # 确保值对应有效的操作点
                special_operations.append(value)

    valid_operations = valid_operations + special_operations

    try:
        for point_name in valid_operations:
            if point_name in point_mapping:
                x, y = point_mapping[point_name]
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(1)  # 可以根据需要调整等待时间

                if point_name in ["字体选择"]:
                    x_color1, y_color1 = point_mapping["字体选择"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 增加延迟时间
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('enter')

                elif point_name in ["字号大小"]:
                    x_color1, y_color1 = point_mapping["字号大小"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 增加延迟时间
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('enter')

                elif point_name == "字体颜色":
                    x_color1, y_color1 = point_mapping["字体颜色"]
                    pyautogui.moveTo(x_color1, y_color1, duration=0.3)
                    pyautogui.click()
                    pyautogui.moveRel(0, 570, duration=0.3)
                    pyautogui.click()
                    x_arrow2, y_arrow2 = point_mapping["字体颜色1"]
                    pyautogui.moveTo(x_arrow2, y_arrow2, duration=0.3)
                    pyautogui.click()
                    x_arrow3, y_arrow3 = point_mapping["字体颜色2"]
                    pyautogui.moveTo(x_arrow3, y_arrow3, duration=0.3)
                    pyautogui.click()
                    for _ in range(10):
                        pyautogui.press('backspace')
                    value = inputs.get(point_name, "")
                    for char in value:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)  # 增加延迟时间
                    time.sleep(0.5)  # 增加延迟确保输入完成
                    pyautogui.press('enter')
                elif point_name == "字体斜体":
                    # 新增逻辑：检查是否需要设置斜体
                    italic_value = inputs.get(point_name, "")
                    if italic_value == "斜体":
                        x_italic, y_italic = point_mapping["字体斜体"]
                        pyautogui.moveTo(x_italic, y_italic, duration=0.3)
                        pyautogui.click()
                elif point_name == "字体加粗":
                    # 新增逻辑：检查是否需要设置加粗
                    bold_value = inputs.get(point_name, "")
                    if bold_value == "加粗":
                        x_bold, y_bold = point_mapping["字体加粗"]
                        pyautogui.moveTo(x_bold, y_bold, duration=0.3)
                        pyautogui.click()

            else:
                return f"Point {point_name} not found in the mapping."
            
        time.sleep(0.5)  
        pyautogui.press('esc')
        return "本格式设置完成，并已退出编辑状态"
    except Exception as e:
        return f"Failed to perform mouse operations: {str(e)}"


if __name__ == "__main__":
    # 示例输入
    inputs_example = {
        "实线": "",
        "实线颜色":"#C8C8C8",
        "圆角大小": "12mm"
    }
    mcp.run(transport='stdio')