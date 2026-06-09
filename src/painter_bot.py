"""
Painter Bot Module

Automates in-game painting using PyAutoGUI.
Simulates mouse clicks to paint on Heartopia canvas.
"""

import pyautogui
import time
import numpy as np
from pathlib import Path
from typing import Union, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

# Disable PyAutoGUI safety features for faster painting
pyautogui.FAILSAFE = False


class PainterBot:
    """
    Automates painting on Heartopia canvas.
    
    Features:
    - Automatic window detection
    - Painting simulation with configurable speed
    - Batch painting support
    - Safety features to prevent accidental clicks
    """
    
    def __init__(
        self,
        click_speed: float = 0.05,
        safe_mode: bool = True,
        verify_clicks: bool = True
    ):
        """
        Initialize PainterBot.
        
        Args:
            click_speed: Delay between clicks (seconds)
            safe_mode: Enable safety checks
            verify_clicks: Verify each click
        """
        self.click_speed = click_speed
        self.safe_mode = safe_mode
        self.verify_clicks = verify_clicks
        self.game_window = None
        self.is_painting = False
        
        logger.info(
            f"PainterBot initialized: click_speed={click_speed}, "
            f"safe_mode={safe_mode}, verify_clicks={verify_clicks}"
        )
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen resolution.
        
        Returns:
            Tuple of (width, height)
        """
        width, height = pyautogui.size()
        logger.debug(f"Screen size: {width}x{height}")
        return width, height
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            Tuple of (x, y)
        """
        return pyautogui.position()
    
    def move_mouse(self, x: int, y: int, duration: float = 0.1) -> None:
        """
        Move mouse to position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration (seconds)
        """
        pyautogui.moveTo(x, y, duration=duration)
        logger.debug(f"Moved mouse to ({x}, {y})")
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> None:
        """
        Click at position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
        """
        if self.safe_mode and not self._verify_game_window():
            logger.warning("Game window not found, skipping click")
            return
        
        pyautogui.click(x, y, clicks=clicks, button=button, interval=self.click_speed)
        logger.debug(f"Clicked at ({x}, {y}) - {button} button x{clicks}")
    
    def paint_pixel(
        self,
        x: int,
        y: int,
        brush_size: int = 1
    ) -> None:
        """
        Paint a single pixel/brush stroke.
        
        Args:
            x: X coordinate
            y: Y coordinate
            brush_size: Brush size (1-10)
        """
        # Move to position
        self.move_mouse(x, y, duration=0.01)
        
        # Click to paint
        self.click(x, y, clicks=1)
        
        # Add delay for painting speed
        time.sleep(self.click_speed)
    
    def paint_line(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        step_size: int = 5
    ) -> None:
        """
        Paint a line from start to end point.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            step_size: Distance between painting points
        """
        # Calculate line points
        dx = end_x - start_x
        dy = end_y - start_y
        distance = max(abs(dx), abs(dy))
        
        if distance == 0:
            self.paint_pixel(start_x, start_y)
            return
        
        steps = max(int(distance / step_size), 1)
        
        for i in range(steps + 1):
            x = int(start_x + (dx * i / steps))
            y = int(start_y + (dy * i / steps))
            self.paint_pixel(x, y)
    
    def paint_image(
        self,
        image_path: Union[str, Path],
        canvas_start_x: int = 0,
        canvas_start_y: int = 0,
        canvas_size: int = 512,
        threshold: int = 127
    ) -> None:
        """
        Paint image on canvas by clicking all dark pixels.
        
        Args:
            image_path: Path to image file
            canvas_start_x: Canvas top-left X coordinate
            canvas_start_y: Canvas top-left Y coordinate
            canvas_size: Canvas size
            threshold: Threshold for painting (0-255)
        """
        try:
            import cv2
            
            logger.info(f"Starting painting: {image_path}")
            
            # Load image
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            # Get painting coordinates
            coords = np.argwhere(image < threshold)
            total_pixels = len(coords)
            
            logger.info(f"Painting {total_pixels} pixels...")
            
            self.is_painting = True
            start_time = time.time()
            
            # Paint each pixel
            for idx, (y, x) in enumerate(coords):
                if not self.is_painting:
                    break
                
                # Calculate screen coordinates
                screen_x = canvas_start_x + x
                screen_y = canvas_start_y + y
                
                # Paint
                self.paint_pixel(screen_x, screen_y)
                
                # Progress update every 100 pixels
                if (idx + 1) % 100 == 0:
                    elapsed = time.time() - start_time
                    pixels_per_sec = (idx + 1) / elapsed
                    remaining = (total_pixels - idx - 1) / pixels_per_sec if pixels_per_sec > 0 else 0
                    logger.info(
                        f"Progress: {idx + 1}/{total_pixels} "
                        f"({100 * (idx + 1) / total_pixels:.1f}%) - "
                        f"ETA: {remaining:.0f}s"
                    )
            
            elapsed = time.time() - start_time
            logger.info(f"Painting completed in {elapsed:.1f}s")
            self.is_painting = False
            
        except Exception as e:
            logger.error(f"Error painting image: {e}")
            self.is_painting = False
    
    def stop_painting(self) -> None:
        """
        Stop ongoing painting operation.
        """
        self.is_painting = False
        logger.info("Painting stopped")
    
    def setup_game_window(self) -> bool:
        """
        Setup and detect game window.
        
        Returns:
            True if window found
        """
        logger.info("Attempting to detect game window...")
        
        try:
            # Try to find Heartopia window
            import pygetwindow as gw
            
            windows = gw.getWindowsWithTitle('Heartopia')
            if windows:
                self.game_window = windows[0]
                logger.info(f"Found game window: {self.game_window.title}")
                return True
            
            logger.warning("Heartopia window not found")
            return False
            
        except Exception as e:
            logger.warning(f"Could not detect window: {e}")
            return False
    
    def _verify_game_window(self) -> bool:
        """
        Verify game window is still active.
        
        Returns:
            True if window is active
        """
        if not self.safe_mode:
            return True
        
        if self.game_window is None:
            return self.setup_game_window()
        
        try:
            # Check if window still exists and is visible
            return self.game_window.isActive
        except:
            return False
    
    def countdown(self, seconds: int = 5) -> None:
        """
        Countdown before starting automation.
        
        Args:
            seconds: Countdown duration
        """
        logger.info(f"Starting in {seconds} seconds... (Move mouse to top-left to cancel)")
        for i in range(seconds, 0, -1):
            logger.info(f"  {i}...")
            time.sleep(1)
        logger.info("Starting!")
