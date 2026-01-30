# Add lifespan support for startup/shutdown with strong typing
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import base64
import io
import os
import tempfile
from typing import Optional, Tuple

import pyautogui

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
mcp = FastMCP("LocalPlay", dependencies=["pyautogui"], lifespan=lifespan, log_level='ERROR')


@mcp.tool()
def move_mouse(ctx: Context, x: int, y: int, duration: float = 0.5, click: bool = False, button: str = 'left') -> str:
    """
    Move the mouse to a specified position
    
    Parameters:
    - x: Target X coordinate
    - y: Target Y coordinate
    - duration: Movement duration (seconds), default 0.5 seconds
    - click: Whether to click at the target position, default False
    - button: Mouse button, options: 'left', 'right', 'middle', default is 'left'
    
    Returns:
    - Description of the operation result
    """
    try:
        # Move the mouse
        pyautogui.moveTo(x, y, duration=duration)
        
        # Click if needed
        if click:
            pyautogui.click(x, y, button=button)
            return f"Mouse moved to position ({x}, {y}) and clicked with {button} button"
        else:
            return f"Mouse moved to position ({x}, {y})"
    except Exception as e:
        return f"Mouse movement failed: {str(e)}"


@mcp.tool()
def mouse_click(ctx: Context, x: Optional[int] = None, y: Optional[int] = None, 
               button: str = 'left', clicks: int = 1, interval: float = 0.1) -> str:
    """
    Perform a mouse click operation
    
    Parameters:
    - x: Optional, X coordinate of the click position, if not provided clicks at current mouse position
    - y: Optional, Y coordinate of the click position, if not provided clicks at current mouse position
    - button: Mouse button, options: 'left', 'right', 'middle', default is 'left'
    - clicks: Number of clicks, default is 1
    - interval: Interval time between multiple clicks (seconds), default 0.1 seconds
    
    Returns:
    - Description of the operation result
    """
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button, clicks=clicks, interval=interval)
            position_str = f"position ({x}, {y})"
        else:
            pyautogui.click(button=button, clicks=clicks, interval=interval)
            current_pos = pyautogui.position()
            position_str = f"current position ({current_pos.x}, {current_pos.y})"
        
        button_name = {'left': 'left', 'right': 'right', 'middle': 'middle'}.get(button, button)
        return f"Clicked {clicks} time(s) with {button_name} button at {position_str}"
    except Exception as e:
        return f"Mouse click failed: {str(e)}"


@mcp.tool()
def mouse_drag(ctx: Context, start_x: int, start_y: int, end_x: int, end_y: int, 
              button: str = 'left', duration: float = 0.5) -> str:
    """
    Perform a mouse drag operation
    
    Parameters:
    - start_x: Starting position X coordinate
    - start_y: Starting position Y coordinate
    - end_x: Ending position X coordinate
    - end_y: Ending position Y coordinate
    - button: Mouse button for dragging, options: 'left', 'right', 'middle', default is 'left'
    - duration: Drag duration (seconds), default 0.5 seconds
    
    Returns:
    - Description of the operation result
    """
    try:
        # Move to starting position
        pyautogui.moveTo(start_x, start_y)
        
        # Perform drag operation
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
        
        button_name = {'left': 'left', 'right': 'right', 'middle': 'middle'}.get(button, button)
        return f"Dragged with {button_name} button from position ({start_x}, {start_y}) to position ({end_x}, {end_y})"
    except Exception as e:
        return f"Mouse drag failed: {str(e)}"


@mcp.tool()
def mouse_scroll(ctx: Context, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> str:
    """
    Scroll the mouse wheel
    
    Parameters:
    - clicks: Number of scroll clicks, positive scrolls up, negative scrolls down
    - x: Optional, X coordinate of the scroll position, if not provided scrolls at current mouse position
    - y: Optional, Y coordinate of the scroll position, if not provided scrolls at current mouse position
    
    Returns:
    - Description of the operation result
    """
    try:
        # If coordinates are provided, move to specified position first
        if x is not None and y is not None:
            pyautogui.moveTo(x, y)
            position_str = f"position ({x}, {y})"
        else:
            current_pos = pyautogui.position()
            position_str = f"current position ({current_pos.x}, {current_pos.y})"
        
        # Perform scroll
        pyautogui.scroll(clicks)
        
        direction = "up" if clicks > 0 else "down"
        abs_clicks = abs(clicks)
        return f"Scrolled {direction} {abs_clicks} time(s) at {position_str}"
    except Exception as e:
        return f"Mouse scroll operation failed: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')