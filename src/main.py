"""
Heartopia Auto-Painter - Main CLI Entry Point

Command-line interface for image processing and automation.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from .image_processor import ImageProcessor
from .anime_converter import AnimeConverter
from .heartopia_adapter import HeartopiaAdapter
from .painter_bot import PainterBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_image(
    input_path: str,
    output_path: str,
    style: str = 'lineart',
    canvas_size: int = 512,
    enhance: bool = True
) -> bool:
    """
    Process image and save result.
    
    Args:
        input_path: Input image path
        output_path: Output image path
        style: Processing style ('lineart', 'anime', 'cartoon')
        canvas_size: Canvas size
        enhance: Enable enhancement
        
    Returns:
        True if successful
    """
    try:
        logger.info(f"Processing: {input_path} -> {output_path}")
        
        # Initialize processors
        processor = ImageProcessor(canvas_size=canvas_size)
        adapter = HeartopiaAdapter(canvas_size=canvas_size)
        
        # Extract line art
        if style == 'lineart':
            line_art = processor.extract_line_art(input_path)
        else:
            logger.warning(f"Style '{style}' not implemented, using lineart")
            line_art = processor.extract_line_art(input_path)
        
        # Adapt for Heartopia
        if enhance:
            adapted = adapter.adapt_for_heartopia(line_art)
        else:
            adapted = adapter.ensure_canvas_size(line_art)
        
        # Validate
        is_valid, issues = adapter.validate_for_heartopia(adapted)
        if not is_valid:
            logger.warning(f"Validation issues: {issues}")
        
        # Save
        processor.save_image(adapted, output_path)
        logger.info("Processing completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return False


def paint_image(
    image_path: str,
    canvas_start_x: int = 0,
    canvas_start_y: int = 0,
    canvas_size: int = 512,
    click_speed: float = 0.05,
    safe_mode: bool = True,
    countdown: int = 5
) -> bool:
    """
    Automate painting on Heartopia canvas.
    
    Args:
        image_path: Image to paint
        canvas_start_x: Canvas X position
        canvas_start_y: Canvas Y position
        canvas_size: Canvas size
        click_speed: Click delay
        safe_mode: Enable safety checks
        countdown: Countdown before start
        
    Returns:
        True if successful
    """
    try:
        logger.info(f"Initializing painting automation: {image_path}")
        
        # Initialize bot
        bot = PainterBot(
            click_speed=click_speed,
            safe_mode=safe_mode,
            verify_clicks=True
        )
        
        # Setup game window
        if safe_mode:
            if not bot.setup_game_window():
                logger.error("Could not detect game window. Disable --no-safe-mode to continue anyway.")
                return False
        
        # Countdown
        if countdown > 0:
            bot.countdown(countdown)
        
        # Start painting
        bot.paint_image(
            image_path,
            canvas_start_x=canvas_start_x,
            canvas_start_y=canvas_start_y,
            canvas_size=canvas_size
        )
        
        logger.info("Painting automation completed")
        return True
        
    except Exception as e:
        logger.error(f"Error in painting automation: {e}")
        return False


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description='Heartopia Auto-Painter - AI-powered automatic painting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract line art from image
  python -m src.main process --input anime.jpg --output line_art.png --style lineart
  
  # Paint extracted image on Heartopia
  python -m src.main paint --image line_art.png --click-speed 0.05
  
  # Convert anime image to painting style
  python -m src.main process --input naruto.jpg --output painted.png --style anime
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process image')
    process_parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input image path'
    )
    process_parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output image path'
    )
    process_parser.add_argument(
        '--style', '-s',
        choices=['lineart', 'anime', 'cartoon'],
        default='lineart',
        help='Processing style (default: lineart)'
    )
    process_parser.add_argument(
        '--canvas-size',
        type=int,
        choices=[512, 1024],
        default=512,
        help='Canvas size (default: 512)'
    )
    process_parser.add_argument(
        '--no-enhance',
        action='store_true',
        help='Disable image enhancement'
    )
    
    # Paint command
    paint_parser = subparsers.add_parser('paint', help='Paint on Heartopia')
    paint_parser.add_argument(
        '--image', '-i',
        required=True,
        help='Image to paint'
    )
    paint_parser.add_argument(
        '--canvas-x',
        type=int,
        default=0,
        help='Canvas top-left X coordinate (default: 0)'
    )
    paint_parser.add_argument(
        '--canvas-y',
        type=int,
        default=0,
        help='Canvas top-left Y coordinate (default: 0)'
    )
    paint_parser.add_argument(
        '--canvas-size',
        type=int,
        choices=[512, 1024],
        default=512,
        help='Canvas size (default: 512)'
    )
    paint_parser.add_argument(
        '--click-speed',
        type=float,
        default=0.05,
        help='Delay between clicks in seconds (default: 0.05)'
    )
    paint_parser.add_argument(
        '--no-safe-mode',
        action='store_true',
        help='Disable safety checks'
    )
    paint_parser.add_argument(
        '--countdown',
        type=int,
        default=5,
        help='Countdown before start in seconds (default: 5)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'process':
        success = process_image(
            input_path=args.input,
            output_path=args.output,
            style=args.style,
            canvas_size=args.canvas_size,
            enhance=not args.no_enhance
        )
    elif args.command == 'paint':
        success = paint_image(
            image_path=args.image,
            canvas_start_x=args.canvas_x,
            canvas_start_y=args.canvas_y,
            canvas_size=args.canvas_size,
            click_speed=args.click_speed,
            safe_mode=not args.no_safe_mode,
            countdown=args.countdown
        )
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
