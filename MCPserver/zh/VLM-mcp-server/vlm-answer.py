from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import os
import base64
from openai import OpenAI
from typing import Optional
from mcp.server.fastmcp import Context, FastMCP
from openai import AzureOpenAI


# 模型名称全局常量
# MODEL_NAME = "qwen-vl-max-2025-04-08"
# MODEL_NAME = "claude-opus-4-20250514"
# MODEL_NAME = "llama-4-maverick"
# MODEL_NAME = "gpt-4o"
# MODEL_NAME = "gpt-4.1"
MODEL_NAME = "o3"
# MODEL_NAME = "gemini-2.5-pro"
# MODEL_NAME = "gpt-5"

client = OpenAI(                                                            
    api_key="k",
    base_url="",
)

client = AzureOpenAI(
    azure_endpoint = "/",
    api_key='',
    api_version=""
)

def encode_image(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Failed to load image: {str(e)}")
        return None


# 初始化消息列表, 用于保存历史对话
messages = []

# 生命周期管理
@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    print("Starting Chat service...")
    try:
        yield
    finally:
        print("Shutting down Chat service...")

# 创建 FastMCP 实例
mcp = FastMCP("ChatService", dependencies=["openai"], lifespan=lifespan, log_level='ERROR')
    

@mcp.tool()
def ask_with_images(ctx: Context, type_m:int ,screenshot_image_path: Optional[str] = None, reference_image_path: Optional[str] = None) -> str:
    """
    根据参考图像和/或当前屏幕截图生成下一步绘图指令(有参考图像输入模式, 屏幕截图不是参考图)。
    
    参数:
    - ctx: 科研绘图绘制。
    - type_m: 1/2  1代表初次绘制, 2代表继续绘制。    
    - screenshot_image_path: 当前屏幕截图路径(可选)
    - reference_image_path: 参考图像路径(可选)
    
    返回:
    - 大模型生成的绘图指令
    
    """
# t2i:
    t2i_image_caption_1="Create an illustration of a residual neural ..."
# ti2i:
    ti2i_image_caption_1="The content of the scientific illustration is as follows: ..."






    
    question_1 = (f"{t2i_image_caption_1},你为我严格按照这个图像的描述来设计图片，不能虚构补充任何不存在的组件, 你只需要按照下面的要求, 输出你的设计步骤即可,"
                f"需要绘制的详细一些, 图像的配色和字体需要你自行设计, 需要保证配色统一和谐, 字体统一并且与图形大小相配并且配色容易辨认"
                f"你的输出要符合以下结构化输出示例，******注意: 所有设计元素必须保持在400<x<2000;400<y<1300这个坐标范围内!!!*******"
                f"******注意: 所有设计元素必须保持在400<x<2000;400<y<1300这个坐标范围内!!!*************注意: 所有设计元素必须保持在400<x<2000;400<y<1300这个坐标范围内!!!*************注意: 所有设计元素必须保持在400<x<2000;400<y<1300这个坐标范围内!!!*******"
                f"*********这是一条完整的模块绘制输出样例:(****注意：绘制模块时，可以输出文本内容****)"
                f"- **形状:** 矩形(可选范围:矩形, 圆形, 圆柱, 立方体, 任意形状的闭合图形[如五角星, 三角形, 平行四边形, 梯形, 六边形等等],其中圆柱和立方体的大小单位是毫米, 其他图形的大小单位是像素，一毫米约为5像素)"
                f"- **图形起始:** (-, -)"
                f"- **图形中间点:** (-, -)(-, -)(-, -)(-, -)(如果为矩形和圆形, 则不需要中间点, 如果为任意闭合图形则需要输出中间经过的各个点坐标)"
                f"- **图形结束:** (-, -)"
                f"- **是否填充:** 纯色填充(可选范围:无填充, 纯色填充，***必填项不可省略***)"
                f"- **填充颜色:** #FFD700(16位色彩表示)"
                f"- **填充透明度:** --(可选范围:0-60)"
                f"- **线条类型:** 实线(只能选择实线)"
                f"- **实线颜色:** #FFD700(16位色彩表示)"
                f"- **实线透明度:** --(可选范围:0-60,***不能超过60***)"
                f"- **线条宽度:** --(可选范围:0-10)"
                f"- **线条圆角:** --mm(可选范围:0-10, 必须附带单位mm)"
                f"- **文本内容:** --(非必要，若无本文内容，后续字体也不必设置)"
                f"- **字体选择:** Comic Sans MS"
                f"- **字号大小:** --(可选范围:8-24)"
                f"- **字体颜色:** #FFD700(16位色彩表示)"
                f"- **字体斜体:** 斜体(可选范围:斜体, 非斜体)"
                f"- **字体加粗:** 加粗(可选范围:加粗, 非加粗)"
                f"********这是一条完整的线条绘制输出样例:(****注意：绘制线条时，不可以输出文本内容, 文本内容需要在其他位置添加****)"
                f"- **形状:** 直线(可选范围:直线, 曲线, 连续直线)"
                f"- **线条起始:** (-, -)"
                f"- **线条中间点:** (-, -)(-, -)(-, -)(-, -)(如果为直线, 则不需要中间点连线, 如果为曲线或者连续直线则需要输出中间经过的各个点坐标)"
                f"- **线条结束:** (-, -)"
                f"- **线条类型:** 实线(只能选择实线)"
                f"- **实线颜色:** #FFD700(16位色彩表示)"
                f"- **实线透明度:** --(可选范围:0-60)"
                f"- **线条宽度:** --(可选范围:0-10)"
                f"- **线条圆角:** --mm(可选范围:0-10, 必须附带单位mm)"
                f"- **是否箭头:** 箭头(可选范围:箭头, 无箭头)"
                f"*********这是一条完整的在其他位置做文本添加输出样例:"
                f"- **文本位置:** (-, -)"
                f"- **文本框大小：** (-, -)"
                f"- **文本内容:** --"
                f"- **字体选择:** Comic Sans MS"
                f"- **字号大小:** --(可选范围:8-24)"
                f"- **字体颜色:** #FFD700(16位色彩表示)"
                f"- **字体斜体:** 斜体(可选范围:斜体, 非斜体)"
                f"- **字体加粗:** 加粗(可选范围:加粗, 非加粗)"
                f"注意, 你输出的文本内容只能是英文, 字体必须是'Comic Sans MS',注意合理安排文本框大小和字体大小, 上面输出模式中补充的内容不需要输出, 这个设计工作需要分多个步骤进行, "
                f"一次只可以输出一到三个组件(模块, 连接线, 文本等等)的设计工作,一次只可以输出一到三个组件(模块, 连接线, 文本等等)的设计工作,一次只可以输出一到三个组件(模块, 连接线, 文本等等)的设计工作"
                f"如果有图像输入, 这个图像是我为你找的一个参考图像, 你需要根据这个参考图像以及上面的设计任务来做插图的设计"
                f"你设计的过程中不需要询问我的意见, 你拥有100%主动权, 想怎么设计就怎么设计, 你也可以任意的扩充上面的绘图需求, 我的目的是绘制一幅能应用在论文中的专业的科研绘图"
                f"你设计的绘图范围要保持在*****400<x<2000;400<y<1300*****这个范围内!!!, 你要合理的控制每个模块的大小, ***不要超过这个范围***, 你要保证每个模块的大小和位置都合理, 并且每个模块之间的间距也合理"
                f"***使用中文输出上述设计内容***")
    
    question_2 = (f"{t2i_image_caption_1}"
                f"第一幅图是当前根据你的设计进行绘制的结果, 你需要分析当前绘制进度和最终目标的差距, 然后根据这个差距来继续设计下一步的行动,"
                f"前一步绘制内容已经操作完毕, 你需要分析当前绘制进度和最终目标的差距, 然后根据这个差距来继续设计下一步的行动,"
                f"如果有第二幅图输入的话, 那么这幅图就是我给你找的一个参考图像, 你需要根据这个参考图像以及上面的设计任务来做插图的设计"
                f"并且你需要仔细分析已经绘制的内容，没有必要改正任何错误，继续往下推进就好，因为可能存在设计的冲突，直到你认为已经绘制完毕了, 这时候你可以输出'全部结束', 并且只需要输出'全部结束'四个字就好"
                f"没有必要修正错误，你的任务是快速推进设计的进程！！！"
                f"除上述的一些工具以外, 你还可以对图中元素进行大小修改，复制, 移动, 删除的操作, 输出示例为:将(-, -)位置(-,-)范围内的元素复制到(-, -);将(-, -)位置(-,-)范围内的元素移动到(-, -)；将(-, -)位置(-,-)范围内的元素删除"
                f"***注意***:设计上述操作的时候输出位置坐标一定是目标模块的几何中心坐标，否则会造成目标位置的偏移"
                f"*********这是一条大小修改输出样例:"
                f"把(-,-)位置(-,-)范围内的元素大小修改为(-,-)"
                f"*********这是一条复制输出样例:"
                f"把(-,-)位置(-,-)范围内的元素复制到(-,-)"
                f"*********这是一条移动输出样例:"
                f"把(-,-)位置(-,-)范围内的元素移动到(-,-)"
                f"*********这是一条删除输出样例:"
                f"把(-,-)位置(-,-)范围内的元素删除"
                f"因为没有对图中元素修改的工具, 你可以选择将元素删除然后重新绘制"
                f"你还可以在图像中添加创意的icon, 你可以选择的icon有: chatgpt, correct, deepseek, error, fire, image, qwen, snow, text, robot, light, gear, network, book, medal"
                f"*********这是一条在任意位置插入任意大小的创意图标输出样例:"
                f"- **类型:** icon"
                f"- **图标名称:** gear"
                f"- **位置:** (-, -)"
                f"- **大小:** (-, -)(为图标的长和宽单位是毫米，一毫米约为5像素值，注意换算关系)"              
                f"你设计的过程中不需要询问我的意见, 你拥有100%主动权, 想怎么设计就怎么设计, 你也可以任意的扩充上面的绘图需求, 我的目的是绘制一幅能应用在论文中的专业的科研绘图"
                f"一次只可以输出一到三个组件(模块, 连接线, 文本等等)的设计工作,一次只可以输出一到三个组件(模块, 连接线, 文本等等)的设计工作,一次只可以输出一到三个组件(模块, 连接线, 文本等等)的设计工作"
                f"同样你需要保持原来的输出范式, 并且绘图范围要保持在*****400<x<2000;400<y<1300*****这个范围内!!!, 你要合理的控制每个模块的大小, ***不要超过这个范围***, 你要保证每个模块的大小和位置都合理, 并且每个模块之间的间距也合理"
                f"你所有的设计必须严格按照我给你的描述来, 不能有任何多余或者虚构的信息，文本描述是什么内容，你就只能设计什么内容。"
                f"***使用中文输出上述设计内容***")
    
    global messages 

    if str(type_m) == "1":  # 1代表初次绘制
        messages = []  # 清空全局变量
        print("检测到初次绘制，已清空消息列表")
    
    if len(messages) == 0:
        question = question_1
        # test_suffix = f"{MODEL_NAME}测试_1"
    else:
        question = question_2
        # test_suffix = f"{MODEL_NAME}测试_2"
    
    question_test = "对比这两张图片的内容" 

    # 构建完整的问题描述（合并 question 和图像状态信息）
    full_question = question

    # 添加屏幕截图状态
    if screenshot_image_path:
        base64_screenshot_image = encode_image(screenshot_image_path)
        if base64_screenshot_image:
            full_question += "\n\n当前屏幕截图已提供"
        else:
            full_question += "\n\n屏幕截图无法加载"
    else:
        full_question += "\n\n无当前屏幕截图, 基于初始状态生成指令"

    # 添加参考图像状态
    if reference_image_path:
        base64_reference_image = encode_image(reference_image_path)
        if base64_reference_image:
            full_question += "\n\n参考图像已提供"
        else:
            full_question += "\n\n参考图像无法加载"
    else:
        full_question += "\n\n当前无参考图像, 处于自由设计模式"

    # 使用完整的问题描述构建消息内容
    content = [{"type": "text", "text": full_question}]

    # 添加图像数据（保持原有逻辑不变）
    if screenshot_image_path and base64_screenshot_image:
        content.append({
            "type": "image_url", 
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_screenshot_image}",
                "alt_text": "当前绘制进度"
            }
        })

    if reference_image_path and base64_reference_image:
        content.append({
            "type": "image_url", 
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_reference_image}",
                "alt_text": "参考图像（目标效果）"
            }
        })

    
    # 发送请求
    user_message = {"role": "user", "content": content}
    # messages.append(user_message)
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages+[user_message]
        )
        assistant_reply = completion.choices[0].message.content
        # assistant_reply+= test_suffix

        # 提取用户消息中的文本内容（不包含图像）
        text_only_user_content = []
        for item in content:
            if item["type"] == "text":
                text_only_user_content.append(item)

        # messages.append({"role": "assistant", "content": [{"type": "text", "text": assistant_reply}]})

        # 添加不含图像的用户消息到历史记录
        messages.append({"role": "user", "content": text_only_user_content})
        
        # 添加助手回复到历史记录
        messages.append({"role": "assistant", "content": [{"type": "text", "text": assistant_reply}]})

        # 仅保留最近的3次对话（6条消息，因为一次对话包含user和assistant两条消息）
        if len(messages) > 96:
            messages = messages[-96:]

        messages_len=len(messages)
        return assistant_reply
    except Exception as e:
        return f"请求出错:{str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
