"""
Download pre-trained models for Heartopia Auto-Painter

This script downloads necessary AI models for image processing.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging():
    """
    Setup logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def download_models(force: bool = False):
    """
    Download required pre-trained models.
    
    Args:
        force: Force download even if models exist
    """
    setup_logging()
    
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    logger.info(f"Models directory: {models_dir}")
    
    # Model URLs (these are placeholders - in production, use actual model URLs)
    models = {
        'lineart_model.pth': 'https://example.com/lineart_model.pth',
        'animegan2_model.pth': 'https://example.com/animegan2_model.pth',
    }
    
    logger.info(f"Models to download: {list(models.keys())}")
    
    for model_name, model_url in models.items():
        model_path = models_dir / model_name
        
        if model_path.exists() and not force:
            logger.info(f"✓ {model_name} already exists")
            continue
        
        logger.info(f"Downloading {model_name}...")
        
        try:
            import urllib.request
            urllib.request.urlretrieve(model_url, str(model_path))
            logger.info(f"✓ Downloaded {model_name}")
        except Exception as e:
            logger.warning(f"Could not download {model_name}: {e}")
            logger.info(f"Models will be loaded on-demand when needed")
    
    logger.info("Model setup completed!")


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description='Download pre-trained models for Heartopia Auto-Painter'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force download even if models exist'
    )
    
    args = parser.parse_args()
    download_models(force=args.force)


if __name__ == '__main__':
    main()
