# SuperImage - Image Super-Resolution Toolkit

A powerful image super-resolution tool using Real-ESRGAN for upscaling images with high quality.

## Features

- 🚀 **Real-ESRGAN** powered 4x upscaling
- 🎨 Support for general images and anime images
- 🖥️ **Intuitive GUI application** with liquid glass dark theme
- 🔧 Simple CLI interface
- 💾 Automatic model downloading
- ⚡ GPU acceleration (CUDA support)
- 🧩 **Automatic tiled processing** - No VRAM overflow, works with any image size
- 📦 Easy dependency management with `uv`
- 🎯 Batch processing support

## System Requirements

- Python >= 3.12
- CUDA-compatible GPU (recommended)
- Windows / Linux / macOS

## Installation

### 1. Install uv (if not already installed)

```bash
# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the repository

```bash
git clone https://github.com/Koudesuk/SuperImage.git
cd SuperImage
```

### 3. Setup virtual environment and install dependencies

```bash
# Create and activate virtual environment, install all dependencies
uv sync
```

This will:
- Create a `.venv` directory
- Install all required packages including PyTorch with CUDA support
- Set up the project for development

## Usage

SuperImage offers two ways to upscale your images: a **GUI Application** for interactive use and a **CLI** for scripting and automation.

### Option 1: GUI Application (Recommended for Most Users)

The GUI provides an intuitive interface with drag-and-drop support, real-time preview, and batch processing.

#### Launch the GUI

```bash
uv run python app/main.py
```

#### GUI Features

- **Single Image Mode**
  - Drag and drop images or click to browse
  - Real-time preview of upscaled results
  - Visual progress tracking

- **Batch Processing Mode**
  - Select multiple images at once
  - Process all images in one go
  - Monitor progress for each image

- **Settings**
  - Switch between models (General Images / Anime)
  - Configure output directory
  - Adjust advanced parameters (tile size, padding, scale factor)

- **Model Indicator**
  - Top bar shows currently selected model
  - Easy identification of active configuration

#### Using the GUI

1. **Launch the application**
   ```bash
   uv run python app/main.py
   ```

2. **Single Image Upscaling**
   - Drag and drop an image into the left panel, or click to browse
   - Click "⬆ Upscale Image" button
   - View the result in the right panel
   - Images are saved to the configured output directory

3. **Batch Upscaling**
   - Click "📁 Select Multiple Images"
   - Choose multiple images from the file dialog
   - Click "⬆ Upscale All"
   - Monitor progress in the list and progress bar

4. **Configure Settings**
   - Click the ⚙ settings button in the top-right corner
   - Select model type (General Images or Anime/Cartoon)
   - Set output directory
   - Adjust advanced parameters if needed
   - Click "OK" to save

### Option 2: Command Line Interface (For Automation)

The CLI is perfect for scripting, batch processing via shell scripts, and integration into automated workflows.

#### Basic Upscaling

```bash
# Upscale an image (4x default) - Two ways to run:

# Method 1: Direct script execution (shorter)
uv run python scripts/src/cli.py upscale input.jpg output.jpg

# Method 2: Module execution
uv run python -m scripts.src.cli upscale input.jpg output.jpg
```

#### Switching Models

```bash
# Use the default model for general images (RealESRGAN_x4plus)
uv run python scripts/src/cli.py upscale input.jpg output.jpg

# Use the anime model for anime/cartoon images
uv run python scripts/src/cli.py upscale anime.jpg output.jpg --model RealESRGAN_x4plus_anime_6B
```

#### Advanced Options

```bash
# Using direct script execution
uv run python scripts/src/cli.py upscale input.jpg output.jpg \
  --prompt "high quality, detailed, sharp, 4k" \
  --negative-prompt "blurry, low quality, pixelated, artifacts" \
  --steps 50 \
  --guidance 9.0 \
  --noise-level 20
```

**Note:** The `--prompt`, `--negative-prompt`, `--steps`, `--guidance`, and `--noise-level` parameters are kept for API compatibility but are not used by Real-ESRGAN (which doesn't use diffusion models).

#### Enable Verbose Logging

```bash
uv run python scripts/src/cli.py -v upscale input.jpg output.jpg
```

#### CLI Help

```bash
# Show general help
uv run python scripts/src/cli.py --help

# Show upscale command help
uv run python scripts/src/cli.py upscale --help
```

## Supported Models

The tool automatically downloads and uses the following models:

- **RealESRGAN_x4plus** (default) - Best for general images (photos, real-world content)
- **RealESRGAN_x4plus_anime_6B** - Optimized for anime/cartoon images

Models are downloaded to `./models/` directory on first use (~67MB each).

**How to choose:**
- Use `RealESRGAN_x4plus` for photos, textures, and realistic images
- Use `RealESRGAN_x4plus_anime_6B` with `--model` flag for anime, cartoons, and illustrations

## Quick Start Examples

### GUI Workflow

1. **Launch the GUI**
   ```bash
   uv run python app/main.py
   ```

2. **Configure Settings (Optional)**
   - Click ⚙ in the top-right
   - Select model: "General Images" or "Anime/Cartoon"
   - Set output directory
   - Click OK

3. **Upscale Single Image**
   - Drag and drop an image or click the left panel to browse
   - Click "⬆ Upscale Image"
   - View result in the right panel

4. **Batch Processing**
   - Click "📁 Select Multiple Images"
   - Choose images from file dialog
   - Click "⬆ Upscale All"
   - Wait for completion notification

### CLI Workflow

1. **Prepare your image**
   ```bash
   # Place your low-resolution image in the project directory
   cp /path/to/my_image.jpg ./input.jpg
   ```

2. **Upscale the image**
   ```bash
   uv run python scripts/src/cli.py upscale input.jpg output_4x.jpg
   ```

3. **Check the result**
   ```bash
   # Output will be saved as output_4x.jpg with 4x resolution
   ```

## Project Structure

```
SuperImage/
├── app/                        # GUI Application
│   ├── main.py                 # GUI entry point
│   └── src/
│       ├── core/               # Core processing logic
│       │   └── image_processor.py
│       └── ui/                 # UI components
│           ├── main_window.py  # Main window
│           ├── dialogs/        # Settings dialog
│           ├── widgets/        # Custom widgets
│           └── styles/         # Theme stylesheets
├── scripts/                    # CLI Application
│   └── src/
│       ├── cli.py              # Command-line interface
│       └── models/
│           └── real_esrgan.py  # Real-ESRGAN implementation
├── models/                      # Downloaded model weights (auto-created)
├── pyproject.toml              # Project dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Development

### Run Code Quality Checks

```bash
# Check code quality with ruff
uv run ruff check
```

### Install Development Dependencies

All dependencies are already included in `pyproject.toml` and installed via `uv sync`.

## Technical Details

### Dependencies

- **PyTorch** - Deep learning framework (CUDA 12.8)
- **Real-ESRGAN** - Super-resolution model
- **basicsr** - Image restoration framework
- **OpenCV** - Image processing
- **facexlib** - Face enhancement (optional)
- **gfpgan** - Face restoration (optional)

### GPU Memory Optimization

The implementation includes:
- **Automatic tiled processing** (default tile size: 400x400) - Prevents VRAM overflow for any image size
- Lazy model loading (only loads when needed)
- Automatic GPU memory cleanup
- Support for CPU fallback
- No manual configuration required - works out of the box

### Compatibility

- Includes torchvision compatibility shim for newer versions
- Backward compatible API design
- Cross-platform support (Windows, Linux, macOS)

## Troubleshooting

### CUDA Out of Memory

**Note:** Tiled processing is enabled by default (tile size: 400x400), which prevents VRAM overflow for most cases.

If you still encounter GPU memory errors:
1. Close other GPU-intensive applications
2. The tool processes images in tiles automatically
3. The tool will automatically try CPU if GPU fails

### Model Download Issues

If model download fails:
1. Check your internet connection
2. Models are downloaded from GitHub releases
3. Manual download: Place `.pth` files in `./models/` directory

### Import Errors

Make sure you've run `uv sync` to install all dependencies:
```bash
uv sync
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) by Xintao Wang
- [basicsr](https://github.com/XPixelGroup/BasicSR) by XPixelGroup
