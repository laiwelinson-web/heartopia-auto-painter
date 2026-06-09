"""
Image Processing Module

Handles core image processing for line art extraction using OpenCV
and advanced edge detection algorithms.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Union, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Converts images to line art suitable for Heartopia painting.
    
    Supports:
    - Canny edge detection
    - Morphological operations
    - Contrast enhancement (CLAHE)
    - Image resizing and normalization
    """
    
    def __init__(
        self,
        canvas_size: int = 512,
        edge_threshold_min: int = 50,
        edge_threshold_max: int = 150,
        blur_kernel: int = 5
    ):
        """
        Initialize ImageProcessor.
        
        Args:
            canvas_size: Output image size
            edge_threshold_min: Canny edge detection minimum threshold
            edge_threshold_max: Canny edge detection maximum threshold
            blur_kernel: Gaussian blur kernel size (must be odd)
        """
        self.canvas_size = canvas_size
        self.edge_threshold_min = edge_threshold_min
        self.edge_threshold_max = edge_threshold_max
        self.blur_kernel = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        
        logger.info(
            f"ImageProcessor initialized: canvas_size={canvas_size}, "
            f"thresholds=({edge_threshold_min}, {edge_threshold_max})"
        )
    
    def load_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Load image from file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image as numpy array (BGR)
            
        Raises:
            FileNotFoundError: If image file not found
            ValueError: If image cannot be loaded
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = cv2.imread(str(image_path))
        
        if image is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        logger.info(f"Loaded image: {image_path} (shape: {image.shape})")
        return image
    
    def resize_image(self, image: np.ndarray, size: Optional[int] = None) -> np.ndarray:
        """
        Resize image to canvas size while maintaining aspect ratio.
        
        Args:
            image: Input image
            size: Target size (uses self.canvas_size if None)
            
        Returns:
            Resized image
        """
        size = size or self.canvas_size
        height, width = image.shape[:2]
        
        # Calculate scale to fit within canvas
        scale = min(size / width, size / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Pad to exact canvas size with white background
        pad_width = size - new_width
        pad_height = size - new_height
        pad_top = pad_height // 2
        pad_bottom = pad_height - pad_top
        pad_left = pad_width // 2
        pad_right = pad_width - pad_left
        
        padded = cv2.copyMakeBorder(
            resized,
            pad_top, pad_bottom, pad_left, pad_right,
            cv2.BORDER_CONSTANT,
            value=[255, 255, 255]
        )
        
        logger.debug(f"Resized image to {size}x{size}")
        return padded
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert BGR image to grayscale.
        
        Args:
            image: BGR image
            
        Returns:
            Grayscale image
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def apply_clahe(self, gray_image: np.ndarray, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
        """
        Apply Contrast Limited Adaptive Histogram Equalization.
        
        Improves local contrast without over-amplifying noise.
        
        Args:
            gray_image: Grayscale image
            clip_limit: CLAHE clip limit
            tile_size: Tile size for local processing
            
        Returns:
            Enhanced image
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        enhanced = clahe.apply(gray_image)
        logger.debug(f"Applied CLAHE (clip_limit={clip_limit}, tile_size={tile_size})")
        return enhanced
    
    def apply_blur(self, image: np.ndarray, kernel_size: Optional[int] = None) -> np.ndarray:
        """
        Apply Gaussian blur to reduce noise.
        
        Args:
            image: Input image
            kernel_size: Blur kernel size (uses self.blur_kernel if None)
            
        Returns:
            Blurred image
        """
        kernel_size = kernel_size or self.blur_kernel
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        logger.debug(f"Applied Gaussian blur (kernel_size={kernel_size})")
        return blurred
    
    def extract_edges_canny(self, image: np.ndarray) -> np.ndarray:
        """
        Extract edges using Canny edge detection.
        
        Args:
            image: Grayscale image
            
        Returns:
            Edge-detected image (binary)
        """
        edges = cv2.Canny(image, self.edge_threshold_min, self.edge_threshold_max)
        logger.debug(
            f"Canny edge detection: thresholds=({self.edge_threshold_min}, {self.edge_threshold_max})"
        )
        return edges
    
    def apply_morphological_ops(
        self,
        image: np.ndarray,
        operation: str = 'close',
        kernel_size: int = 3
    ) -> np.ndarray:
        """
        Apply morphological operations to enhance line quality.
        
        Args:
            image: Binary image
            operation: 'close', 'open', 'dilate', or 'erode'
            kernel_size: Kernel size
            
        Returns:
            Processed image
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        if operation == 'close':
            result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        elif operation == 'open':
            result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        elif operation == 'dilate':
            result = cv2.dilate(image, kernel, iterations=1)
        elif operation == 'erode':
            result = cv2.erode(image, kernel, iterations=1)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        logger.debug(f"Applied morphological operation: {operation}")
        return result
    
    def invert_colors(self, image: np.ndarray) -> np.ndarray:
        """
        Invert image colors (black lines on white background).
        
        Args:
            image: Input image
            
        Returns:
            Inverted image
        """
        return cv2.bitwise_not(image)
    
    def extract_line_art(
        self,
        image_path: Union[str, Path],
        use_clahe: bool = True,
        use_morphological: bool = True,
        invert: bool = True
    ) -> np.ndarray:
        """
        Complete pipeline: load image and extract line art.
        
        Args:
            image_path: Path to input image
            use_clahe: Apply CLAHE enhancement
            use_morphological: Apply morphological operations
            invert: Invert colors for painting style
            
        Returns:
            Line art image
        """
        logger.info(f"Starting line art extraction: {image_path}")
        
        # Load and resize
        image = self.load_image(image_path)
        image = self.resize_image(image)
        
        # Convert to grayscale
        gray = self.convert_to_grayscale(image)
        
        # Enhance contrast
        if use_clahe:
            gray = self.apply_clahe(gray)
        
        # Blur to reduce noise
        blurred = self.apply_blur(gray)
        
        # Extract edges
        edges = self.extract_edges_canny(blurred)
        
        # Morphological operations
        if use_morphological:
            edges = self.apply_morphological_ops(edges, operation='close', kernel_size=3)
            edges = self.apply_morphological_ops(edges, operation='open', kernel_size=2)
        
        # Invert for painting style
        if invert:
            line_art = self.invert_colors(edges)
        else:
            line_art = edges
        
        logger.info(f"Line art extraction completed (shape: {line_art.shape})")
        return line_art
    
    def save_image(self, image: np.ndarray, output_path: Union[str, Path], quality: int = 95) -> None:
        """
        Save image to file.
        
        Args:
            image: Image to save
            output_path: Output file path
            quality: JPEG quality (1-100)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix.lower() in ['.jpg', '.jpeg']:
            cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        else:
            cv2.imwrite(str(output_path), image)
        
        logger.info(f"Image saved: {output_path}")
    
    def get_image_info(self, image: np.ndarray) -> dict:
        """
        Get image information.
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with image info
        """
        height, width = image.shape[:2]
        channels = 1 if len(image.shape) == 2 else image.shape[2]
        
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'dtype': str(image.dtype),
            'shape': image.shape,
            'size_mb': image.nbytes / (1024 * 1024)
        }
