import pyautogui
import time

# 初始化上一次的鼠标位置
previous_x, previous_y = pyautogui.position()

'''
获取 屏幕尺寸 安装命令 pip install PyAutoGUI
'''
## 获取 屏幕尺寸 Size(width=1610, height=926)
size = pyautogui.size()
print(size)
## 屏幕高度
windows_height = size.height
## 屏幕宽度
windows_width = size.width

try:
    while True:
        # 获取当前鼠标位置
        current_x, current_y = pyautogui.position()

        # 检查鼠标位置是否发生变化
        if current_x != previous_x or current_y != previous_y:
            print(f"鼠标位置已更新：({current_x}, {current_y})")
            # 更新上一次的鼠标位置
            previous_x, previous_y = current_x, current_y

        # 适当延迟以减少 CPU 占用
        time.sleep(0.1)

except KeyboardInterrupt:
    print("程序已停止。")