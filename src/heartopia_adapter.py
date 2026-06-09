"""
Heartopia Adapter Module

Adapts processed images to Heartopia game requirements and formats.
Handles game-specific optimizations and conversions.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Union, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class HeartopiaAdapter:
    """
    Adapts images for Heartopia painting canvas.
    
    Features:
    - Heartopia canvas size optimization (512x512, 1024x1024)
    - Color palette adjustment
    - Line quality optimization for in-game painting
    - Coordinate mapping for automation
    """
    
    # Heartopia supported canvas sizes
    SUPPORTED_SIZES = [512, 1024]
    
    def __init__(
        self,
        canvas_size: int = 512,
        enhance_edges: bool = True,
        remove_background: bool = False
    ):
        """
        Initialize HeartopiaAdapter.
        
        Args:
            canvas_size: Target canvas size (512 or 1024)
            enhance_edges: Enhance line edges for clarity
            remove_background: Remove white background (make transparent)
        """
        if canvas_size not in self.SUPPORTED_SIZES:
            raise ValueError(f"Canvas size must be one of {self.SUPPORTED_SIZES}")
        
        self.canvas_size = canvas_size
        self.enhance_edges = enhance_edges
        self.remove_background = remove_background
        
        logger.info(
            f"HeartopiaAdapter initialized: canvas_size={canvas_size}, "
            f"enhance_edges={enhance_edges}, remove_background={remove_background}"
        )
    
    def ensure_canvas_size(self, image: np.ndarray) -> np.ndarray:
        """
        Ensure image is exactly the target canvas size.
        
        Args:
            image: Input image
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if width == self.canvas_size and height == self.canvas_size:
            return image
        
        # Calculate scaling
        scale = min(self.canvas_size / width, self.canvas_size / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Pad to exact size
        pad_width = self.canvas_size - new_width
        pad_height = self.canvas_size - new_height
        pad_top = pad_height // 2
        pad_bottom = pad_height - pad_top
        pad_left = pad_width // 2
        pad_right = pad_width - pad_left
        
        # Determine pad color based on image type
        if len(image.shape) == 2:
            pad_value = 255  # White for grayscale
        else:
            pad_value = [255, 255, 255]  # White for BGR
        
        padded = cv2.copyMakeBorder(
            resized,
            pad_top, pad_bottom, pad_left, pad_right,
            cv2.BORDER_CONSTANT,
            value=pad_value
        )
        
        logger.debug(f"Ensured canvas size: {self.canvas_size}x{self.canvas_size}")
        return padded
    
    def enhance_line_quality(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance line quality for better painting results.
        
        Args:
            image: Binary line art image
            
        Returns:
            Enhanced image
        """
        if not self.enhance_edges:
            return image
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Threshold to binary
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Dilate to strengthen lines
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        enhanced = cv2.dilate(binary, kernel, iterations=1)
        
        # Optional: thin lines with skeletonization
        # enhanced = cv2.ximgproc.thinning(enhanced)
        
        logger.debug("Enhanced line quality")
        return enhanced
    
    def remove_white_background(self, image: np.ndarray) -> np.ndarray:
        """
        Remove white background and make transparent (RGBA).
        
        Args:
            image: Input image
            
        Returns:
            RGBA image with transparent background
        """
        if not self.remove_background:
            return image
        
        # Ensure BGR
        if len(image.shape) == 2:
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            bgr = image
        
        # Convert to RGBA
        rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
        
        # Create mask for white pixels
        lower_white = np.array([200, 200, 200])
        upper_white = np.array([255, 255, 255])
        mask = cv2.inRange(bgr, lower_white, upper_white)
        
        # Set alpha channel
        rgba[:, :, 3] = 255 - mask
        
        logger.debug("Removed white background")
        return rgba
    
    def adjust_contrast(self, image: np.ndarray, alpha: float = 1.2, beta: float = 10) -> np.ndarray:
        """
        Adjust image contrast using: output = alpha * input + beta
        
        Args:
            image: Input image
            alpha: Contrast control (1.0 = no change)
            beta: Brightness offset
            
        Returns:
            Adjusted image
        """
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        logger.debug(f"Adjusted contrast: alpha={alpha}, beta={beta}")
        return adjusted
    
    def dither_image(
        self,
        image: np.ndarray,
        palette_size: int = 256
    ) -> np.ndarray:
        """
        Apply dithering for color reduction (if needed for Heartopia).
        
        Args:
            image: Input image
            palette_size: Target palette size
            
        Returns:
            Dithered image
        """
        if len(image.shape) != 3:
            return image
        
        # Convert to uint8
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        # K-means color reduction
        data = image.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(data, palette_size, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        dithered = centers[labels.flatten()]
        dithered = dithered.reshape(image.shape)
        
        logger.debug(f"Applied dithering: palette_size={palette_size}")
        return dithered
    
    def extract_painting_coordinates(
        self,
        image: np.ndarray,
        threshold: int = 127
    ) -> list:
        """
        Extract pixel coordinates where painting should occur.
        
        Useful for automation (PyAutoGUI) to know where to click.
        
        Args:
            image: Binary line art image
            threshold: Threshold for line detection
            
        Returns:
            List of (x, y) coordinates
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Threshold
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
        
        # Find coordinates
        coords = np.argwhere(binary > 0)
        
        # Convert to (x, y) format
        painting_coords = [(int(x), int(y)) for y, x in coords]
        
        logger.info(f"Extracted {len(painting_coords)} painting coordinates")
        return painting_coords
    
    def adapt_for_heartopia(
        self,
        image: np.ndarray,
        enhance_lines: bool = True,
        adjust_contrast_val: bool = True
    ) -> np.ndarray:
        """
        Complete adaptation pipeline for Heartopia.
        
        Args:
            image: Input image
            enhance_lines: Enhance line quality
            adjust_contrast_val: Adjust contrast
            
        Returns:
            Heartopia-adapted image
        """
        logger.info("Starting Heartopia adaptation")
        
        # Ensure correct canvas size
        image = self.ensure_canvas_size(image)
        
        # Enhance lines
        if enhance_lines:
            image = self.enhance_line_quality(image)
        
        # Adjust contrast
        if adjust_contrast_val:
            image = self.adjust_contrast(image, alpha=1.2, beta=5)
        
        # Remove background if needed
        if self.remove_background:
            image = self.remove_white_background(image)
        
        logger.info("Heartopia adaptation completed")
        return image
    
    def validate_for_heartopia(self, image: np.ndarray) -> Tuple[bool, list]:
        """
        Validate image compatibility with Heartopia.
        
        Args:
            image: Image to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        height, width = image.shape[:2]
        
        # Check size
        if width != self.canvas_size or height != self.canvas_size:
            issues.append(f"Image size must be {self.canvas_size}x{self.canvas_size}, got {width}x{height}")
        
        # Check for empty image
        if np.all(image == 255):
            issues.append("Image appears to be completely white (empty)")
        
        if np.all(image == 0):
            issues.append("Image appears to be completely black")
        
        # Check data type
        if image.dtype != np.uint8:
            issues.append(f"Image dtype should be uint8, got {image.dtype}")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info("Image validation: PASSED")
        else:
            logger.warning(f"Image validation: FAILED - {issues}")
        
        return is_valid, issues
