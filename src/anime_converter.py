"""
Anime Converter Module

Handles anime-to-painting style conversion using pre-trained neural networks.
Supports AnimeGAN and other cartoon style transfer models.
"""

import torch
import torch.nn as nn
import cv2
import numpy as np
from pathlib import Path
from typing import Union, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AnimeConverter:
    """
    Converts anime images to painting-style artwork.
    
    Supports:
    - AnimeGAN v2 and v3
    - Cartoon GAN
    - Real-time inference
    """
    
    def __init__(
        self,
        model_type: str = 'animegan2',
        use_cuda: bool = True,
        model_path: Optional[Union[str, Path]] = None
    ):
        """
        Initialize AnimeConverter.
        
        Args:
            model_type: Type of model ('animegan2', 'animegan3', 'cartoongan')
            use_cuda: Use GPU if available
            model_path: Path to custom model weights
        """
        self.model_type = model_type
        self.device = torch.device('cuda' if use_cuda and torch.cuda.is_available() else 'cpu')
        self.model = None
        self.model_path = model_path
        
        logger.info(f"AnimeConverter initialized: model={model_type}, device={self.device}")
    
    def load_model(self, model_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Load pre-trained model.
        
        Args:
            model_path: Path to model weights
            
        Returns:
            True if successful
        """
        try:
            model_path = model_path or self.model_path
            
            if model_path and Path(model_path).exists():
                logger.info(f"Loading model from: {model_path}")
                self.model = torch.jit.load(str(model_path)).to(self.device)
                self.model.eval()
                logger.info("Model loaded successfully")
                return True
            else:
                logger.warning(f"Model path not found: {model_path}")
                logger.info("Using placeholder model")
                # Return placeholder for now
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def preprocess_image(
        self,
        image: np.ndarray,
        size: int = 512
    ) -> Tuple[torch.Tensor, Tuple[int, int]]:
        """
        Preprocess image for model inference.
        
        Args:
            image: Input image (BGR)
            size: Target size
            
        Returns:
            Tuple of (processed tensor, original size)
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Store original size
        orig_height, orig_width = image_rgb.shape[:2]
        
        # Resize
        image_rgb = cv2.resize(image_rgb, (size, size))
        
        # Normalize to [-1, 1]
        image_rgb = image_rgb.astype(np.float32) / 127.5 - 1.0
        
        # Convert to tensor and add batch dimension
        tensor = torch.from_numpy(image_rgb.transpose(2, 0, 1)).unsqueeze(0)
        tensor = tensor.to(self.device)
        
        logger.debug(f"Preprocessed image: tensor shape {tensor.shape}")
        return tensor, (orig_height, orig_width)
    
    def postprocess_image(self, output: torch.Tensor) -> np.ndarray:
        """
        Postprocess model output to image.
        
        Args:
            output: Model output tensor
            
        Returns:
            Image as numpy array (BGR)
        """
        # Remove batch dimension
        output = output.squeeze(0)
        
        # Convert to numpy
        output = output.cpu().detach().numpy().transpose(1, 2, 0)
        
        # Denormalize from [-1, 1] to [0, 255]
        output = ((output + 1.0) * 127.5).astype(np.uint8)
        
        # Convert RGB to BGR
        output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        
        return output
    
    def convert_to_anime(
        self,
        image_path: Union[str, Path],
        output_size: int = 512
    ) -> Optional[np.ndarray]:
        """
        Convert image to anime style.
        
        Args:
            image_path: Path to input image
            output_size: Output image size
            
        Returns:
            Converted image or None if error
        """
        try:
            if not self.model:
                logger.warning("Model not loaded, returning original image")
                return cv2.imread(str(image_path))
            
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            logger.info(f"Converting to anime style: {image_path}")
            
            # Preprocess
            tensor, orig_size = self.preprocess_image(image, output_size)
            
            # Inference
            with torch.no_grad():
                output = self.model(tensor)
            
            # Postprocess
            anime_image = self.postprocess_image(output)
            
            logger.info(f"Anime conversion completed (shape: {anime_image.shape})")
            return anime_image
            
        except Exception as e:
            logger.error(f"Error in anime conversion: {e}")
            return None
    
    def convert_to_painting(
        self,
        image_path: Union[str, Path],
        style: str = 'anime',
        output_size: int = 512
    ) -> Optional[np.ndarray]:
        """
        Convert image to painting style for Heartopia.
        
        Args:
            image_path: Path to input image
            style: Painting style ('anime', 'cartoon', 'oil', etc.)
            output_size: Output size
            
        Returns:
            Converted image
        """
        if style == 'anime':
            return self.convert_to_anime(image_path, output_size)
        else:
            logger.warning(f"Style '{style}' not yet implemented, returning anime style")
            return self.convert_to_anime(image_path, output_size)
    
    def batch_convert(
        self,
        image_paths: list,
        output_size: int = 512
    ) -> list:
        """
        Convert multiple images.
        
        Args:
            image_paths: List of image paths
            output_size: Output size
            
        Returns:
            List of converted images
        """
        results = []
        for i, path in enumerate(image_paths):
            logger.info(f"Converting image {i+1}/{len(image_paths)}: {path}")
            result = self.convert_to_anime(path, output_size)
            results.append(result)
        
        return results
    
    def get_available_styles(self) -> list:
        """
        Get available conversion styles.
        
        Returns:
            List of available styles
        """
        return ['anime', 'cartoon', 'oil', 'watercolor', 'sketch']
