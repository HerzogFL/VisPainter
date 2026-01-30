#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pyautogui
import random
import os


pyautogui.FAILSAFE = False

def main():
    """简单的鼠标移动测试"""

    width, height = pyautogui.size()
    print(f"屏幕尺寸: {width} x {height}")
    
    initial_x, initial_y = pyautogui.position()
    print(f"当前鼠标位置: ({initial_x}, {initial_y})")
    
    try:
        center_x, center_y = width // 2, height // 2
        print(f"\n移动到屏幕中心: ({center_x}, {center_y})")
        pyautogui.moveTo(center_x, center_y, duration=1)
        print("移动完成!")
        time.sleep(1)
        
        print("\n开始画正方形...")
        side = 100
        
        start_x = center_x - side // 2
        start_y = center_y - side // 2
        print(f"移动到起始位置: ({start_x}, {start_y})")
        pyautogui.moveTo(start_x, start_y, duration=0.5)
        time.sleep(0.5)
        
        print("画正方形的右边")
        pyautogui.moveTo(start_x + side, start_y, duration=0.5)
        time.sleep(0.5)
        
        print("画正方形的下边")
        pyautogui.moveTo(start_x + side, start_y + side, duration=0.5)
        time.sleep(0.5)
        
        print("画正方形的左边")
        pyautogui.moveTo(start_x, start_y + side, duration=0.5)
        time.sleep(0.5)
        
        print("画正方形的上边（闭合）")
        pyautogui.moveTo(start_x, start_y, duration=0.5)
        time.sleep(1)
        
        for i in range(3):
            rand_x = random.randint(100, width - 100)
            rand_y = random.randint(100, height - 100)
            print(f"\n随机移动 {i+1}/3: 移动到 ({rand_x}, {rand_y})")
            pyautogui.moveTo(rand_x, rand_y, duration=0.5)
            time.sleep(0.5)
            
            curr_x, curr_y = pyautogui.position()
            print(f"当前位置: ({curr_x}, {curr_y})")
        
        print("\n测试截图功能...")
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        screenshot_path = "screenshots/full_screen.png"
        print(f"正在截取全屏截图: {screenshot_path}")
        pyautogui.screenshot(screenshot_path)
        print(f"全屏截图保存成功: {screenshot_path}")
        
        region_path = "screenshots/region.png"
        region = (center_x - 100, center_y - 100, 200, 200) 
        print(f"正在截取区域截图: {region_path}，区域: {region}")
        pyautogui.screenshot(region_path, region=region)
        print(f"区域截图保存成功: {region_path}")
        

        print("\n测试键盘输入功能...")
        pyautogui.moveTo(center_x, center_y, duration=0.5)
        time.sleep(0.5)
        
        print("测试按下ESC键...")
        pyautogui.press('esc')
        time.sleep(1)
        
        print("测试按下Alt+Tab组合键...")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        

        print("测试文本输入...")
        test_text = "这是一个键盘输入测试"
        print(f"正在输入文本: '{test_text}'")
        pyautogui.write(test_text, interval=0.1)  # interval是每个字符间的延迟
        time.sleep(1)
        
        print("按下回车键...")
        pyautogui.press('enter')
        time.sleep(1)

    finally:
        print("\n测试结束，将鼠标移回初始位置")
        pyautogui.moveTo(initial_x, initial_y, duration=0.5)

if __name__ == "__main__":
    print("===== 鼠标、键盘和截图功能测试 =====")
    print("注意: 测试过程中鼠标将移动，键盘将被使用，请不要干扰")
    print("如需中断测试，按 Ctrl+C")
    print("3秒后开始测试...")
    
    try:
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        main()
        print("\n测试成功完成!")
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试出错: {e}")
