#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pyautogui
import random
import os

# Disable failsafe for specific automation requirements
pyautogui.FAILSAFE = False

def main():
    """Simple mouse movement and utility test"""

    width, height = pyautogui.size()
    print(f"Screen size: {width} x {height}")
    
    initial_x, initial_y = pyautogui.position()
    print(f"Current mouse position: ({initial_x}, {initial_y})")
    
    try:
        center_x, center_y = width // 2, height // 2
        print(f"\nMoving to screen center: ({center_x}, {center_y})")
        pyautogui.moveTo(center_x, center_y, duration=1)
        print("Movement complete!")
        time.sleep(1)
        
        print("\nStarting to draw a square...")
        side = 100
        
        start_x = center_x - side // 2
        start_y = center_y - side // 2
        print(f"Moving to starting position: ({start_x}, {start_y})")
        pyautogui.moveTo(start_x, start_y, duration=0.5)
        time.sleep(0.5)
        
        print("Drawing right side of the square")
        pyautogui.moveTo(start_x + side, start_y, duration=0.5)
        time.sleep(0.5)
        
        print("Drawing bottom side of the square")
        pyautogui.moveTo(start_x + side, start_y + side, duration=0.5)
        time.sleep(0.5)
        
        print("Drawing left side of the square")
        pyautogui.moveTo(start_x, start_y + side, duration=0.5)
        time.sleep(0.5)
        
        print("Drawing top side of the square (closing)")
        pyautogui.moveTo(start_x, start_y, duration=0.5)
        time.sleep(1)
        
        for i in range(3):
            rand_x = random.randint(100, width - 100)
            rand_y = random.randint(100, height - 100)
            print(f"\nRandom movement {i+1}/3: Moving to ({rand_x}, {rand_y})")
            pyautogui.moveTo(rand_x, rand_y, duration=0.5)
            time.sleep(0.5)
            
            curr_x, curr_y = pyautogui.position()
            print(f"Current position: ({curr_x}, {curr_y})")
        
        print("\nTesting screenshot functionality...")
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        screenshot_path = "screenshots/full_screen.png"
        print(f"Taking full screen screenshot: {screenshot_path}")
        pyautogui.screenshot(screenshot_path)
        print(f"Full screen screenshot saved successfully: {screenshot_path}")
        
        region_path = "screenshots/region.png"
        region = (center_x - 100, center_y - 100, 200, 200) 
        print(f"Taking region screenshot: {region_path}, region: {region}")
        pyautogui.screenshot(region_path, region=region)
        print(f"Region screenshot saved successfully: {region_path}")
        
        print("\nTesting keyboard input functionality...")
        pyautogui.moveTo(center_x, center_y, duration=0.5)
        time.sleep(0.5)
        
        print("Testing ESC key press...")
        pyautogui.press('esc')
        time.sleep(1)
        
        print("Testing Alt+Tab hotkey...")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        
        print("Testing text input...")
        test_text = "This is a keyboard input test"
        print(f"Typing text: '{test_text}'")
        pyautogui.write(test_text, interval=0.1)  # interval is the delay between characters
        time.sleep(1)
        
        print("Pressing Enter key...")
        pyautogui.press('enter')
        time.sleep(1)

    finally:
        print("\nTest finished. Returning mouse to initial position.")
        pyautogui.moveTo(initial_x, initial_y, duration=0.5)

if __name__ == "__main__":
    print("===== Mouse, Keyboard, and Screenshot Functionality Test =====")
    print("Note: The mouse will move and the keyboard will be used during the test. Please do not interfere.")
    print("To interrupt the test, press Ctrl+C")
    print("Starting test in 3 seconds...")
    
    try:
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        main()
        print("\nTest completed successfully!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")