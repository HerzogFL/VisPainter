import pyautogui
import time

# Initialize the previous mouse position
previous_x, previous_y = pyautogui.position()

'''
Get screen dimensions. Installation command: pip install PyAutoGUI
'''
## Get screen dimensions: Size(width=1610, height=926)
size = pyautogui.size()
print(size)
## Screen height
windows_height = size.height
## Screen width
windows_width = size.width

try:
    while True:
        # Get current mouse position
        current_x, current_y = pyautogui.position()

        # Check if the mouse position has changed
        if current_x != previous_x or current_y != previous_y:
            print(f"Mouse position updated: ({current_x}, {current_y})")
            # Update the previous mouse position
            previous_x, previous_y = current_x, current_y

        # Appropriate delay to reduce CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Program stopped.")