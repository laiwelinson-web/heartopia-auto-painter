# Heartopia Auto-Painter 🎨

A free, open-source Python tool that automatically converts anime and landscape images into paintings for the Heartopia game. No more manual painting - let AI do the work!

## Features

✨ **Automatic Image-to-Painting Conversion**
- Convert anime images (Naruto, One Piece, etc.) to paintable line art
- Convert landscape photos to stylized paintings
- Support for complex detailed images

🤖 **AI-Powered Processing**
- Deep learning-based line art extraction
- Anime-optimized conversion using AnimeGAN
- Edge detection and image enhancement

🎮 **Heartopia-Compatible Output**
- Generates images optimized for Heartopia's painting canvas
- Adjustable resolution and detail levels
- Multiple output formats

🖱️ **Automated Painting (Optional)**
- PyAutoGUI integration for in-game automation
- Batch processing support
- Click-to-paint simulation

## Installation

### Prerequisites
- Python 3.10+
- Windows OS
- CUDA-capable GPU (recommended, but CPU works too)

### Setup

```bash
# Clone the repository
git clone https://github.com/laiwelinson-web/heartopia-auto-painter.git
cd heartopia-auto-painter

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download pre-trained models
python scripts/download_models.py
```

## Quick Start

### GUI Application
```bash
python gui/app.py
```

### Command Line
```bash
python src/main.py --input image.jpg --output output.png --style anime
```

## How It Works

### 1. **Image Preprocessing**
   - Load and normalize input image
   - Resize to optimal canvas size (512x512 recommended)
   - Apply blur and contrast enhancement

### 2. **Line Art Extraction**
   - Use edge detection (Canny algorithm)
   - Neural network-based sketch extraction
   - Remove noise and enhance lines

### 3. **Anime Conversion** (Optional)
   - Apply AnimeGAN for cartoon/anime style
   - Preserve details and edge clarity
   - Adjust color saturation if needed

### 4. **Heartopia Adaptation**
   - Convert to game-compatible format
   - Optimize for painting canvas resolution
   - Generate painting coordinates

### 5. **Automated Painting** (Optional)
   - Simulate mouse clicks on in-game canvas
   - Paint pixel-by-pixel or brush stroke simulation
   - Real-time progress tracking

## Usage Examples

### Basic Conversion
```python
from src.image_processor import ImageProcessor

processor = ImageProcessor()
line_art = processor.extract_line_art('anime.jpg')
line_art.save('output_line_art.png')
```

### Anime Image Processing
```python
from src.anime_converter import AnimeConverter

converter = AnimeConverter()
painted = converter.convert_to_painting('naruto.jpg')
painted.save('output_painted.png')
```

### Auto-Painting
```python
from src.painter_bot import PainterBot

bot = PainterBot()
bot.setup_game_window()  # Position game window
bot.paint_image('output_line_art.png', speed='normal')
```

## Supported Image Types

- **Anime**: Naruto, One Piece, Attack on Titan, etc.
- **Landscape**: Mountains, forests, water scenes
- **Complex scenes**: Multiple characters, detailed backgrounds
- **Formats**: JPG, PNG, BMP, WebP

## Configuration

Edit `config.yaml` to customize:

```yaml
image:
  canvas_size: 512
  edge_threshold_min: 50
  edge_threshold_max: 150
  blur_kernel: 5

ai:
  use_cuda: true
  anime_gan_model: 'animegan2'
  line_art_model: 'lineart'

automation:
  click_speed: 0.05  # seconds between clicks
  detection_sensitivity: 0.8
  safe_mode: true  # Prevents accidental clicks
```

## Project Structure

```
heartopia-auto-painter/
├── src/
│   ├── __init__.py
│   ├── image_processor.py      # Core image processing
│   ├── anime_converter.py      # AnimeGAN integration
│   ├── heartopia_adapter.py    # Game-specific formatting
│   ├── painter_bot.py          # PyAutoGUI automation
│   └── main.py                 # CLI entry point
│
├── gui/
│   ├── __init__.py
│   └── app.py                  # Tkinter GUI application
│
├── models/                      # Pre-trained model weights
│   ├── lineart_model.pth
│   └── animegan2_model.pth
│
├── scripts/
│   └── download_models.py      # Download required models
│
├── examples/
│   ├── input_samples/          # Example images
│   └── output_samples/         # Expected outputs
│
├── tests/
│   └── test_processor.py
│
├── config.yaml
├── requirements.txt
├── setup.py
└── README.md
```

## Performance

| Feature | Speed | Quality |
|---------|-------|----------|
| Line Art Extraction | ~1-2 sec | High |
| AnimeGAN Conversion | ~3-5 sec | Very High |
| Heartopia Adaptation | <1 sec | Perfect |
| Auto-Painting (512x512) | ~2-5 min | Real-time |

*Times based on NVIDIA GTX 1080 GPU. CPU times will be 3-5x longer.*

## Known Limitations

⚠️ **Important Disclaimers**:
1. **Terms of Service**: Using automation macros in Heartopia may violate TOS. Use at your own risk.
2. **Game Detection**: Anti-cheat may flag automated painting. Keep frequency reasonable.
3. **Image Quality**: Very high-resolution images may lose detail. Optimize inputs to 512x512-1024x1024.
4. **Anime Styles**: Works best with high-quality anime art. Manga scans may need preprocessing.

## Troubleshooting

### Models not loading
```bash
python scripts/download_models.py --force
```

### Poor line art quality
- Increase `edge_threshold_max` in config.yaml
- Try different blur_kernel values (3, 5, 7, 9)
- Pre-process image brightness/contrast

### Automation not working
- Ensure game window is in focus
- Run as Administrator (Windows)
- Check Heartopia painting canvas is visible

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -m 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open Pull Request

## Roadmap

- [ ] WebP and AVIF support
- [ ] Real-time preview in GUI
- [ ] Model fine-tuning for better anime detection
- [ ] Multi-language support
- [ ] Performance optimizations for CPU-only systems
- [ ] Video-to-painting sequence generation

## License

MIT License - See LICENSE file for details

## Disclaimer

**This tool is for educational purposes.** Using automation software with online games may:
- Violate game Terms of Service
- Result in account suspension or ban
- Trigger anti-cheat detection

Use responsibly and check your game's policies before deploying automation features.

## Support

- **Issues**: Open an issue on GitHub
- **Questions**: Start a discussion
- **Community**: Join the Heartopia modding communities

---

Made with ❤️ for Heartopia players who want to paint smarter, not harder.

**⭐ Star this repo if you find it useful!**