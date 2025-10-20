"""Real-ESRGAN image super-resolution implementation."""

from __future__ import annotations

import gc
import logging
import sys
import types
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import torch

# Fix for torchvision compatibility with newer versions
# torchvision.transforms.functional_tensor was deprecated and removed
# Create a compatibility shim for basicsr
try:
    from torchvision.transforms import functional_tensor
except ImportError:
    from torchvision.transforms.functional import rgb_to_grayscale
    functional_tensor = types.ModuleType("torchvision.transforms.functional_tensor")
    functional_tensor.rgb_to_grayscale = rgb_to_grayscale
    sys.modules["torchvision.transforms.functional_tensor"] = functional_tensor

from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

logger = logging.getLogger(__name__)


# Model configurations mapping
MODEL_CONFIGS = {
    "RealESRGAN_x4plus": {
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        "scale": 4,
        "num_block": 23,
    },
    "RealESRGAN_x4plus_anime_6B": {
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
        "scale": 4,
        "num_block": 6,
    },
}


class RealESRGANUpscaler:
    """Simple and efficient image super-resolution using Real-ESRGAN."""
    
    def __init__(
        self,
        model_name: str = "RealESRGAN_x4plus",
        device: Optional[str] = None,
        torch_dtype: torch.dtype = torch.float16,
        tile: int = 400,
        tile_pad: int = 10,
        pre_pad: int = 0,
    ):
        """Initialize the upscaler.
        
        Args:
            model_name: Model name (RealESRGAN_x4plus or RealESRGAN_x4plus_anime_6B)
            device: Target device ('cuda', 'cpu', or None for auto)
            torch_dtype: Tensor dtype for memory efficiency
            tile: Tile size for processing images (default: 400, prevents VRAM overflow)
            tile_pad: Padding for tiles to reduce seams (default: 10)
            pre_pad: Pre-padding size (default: 0)
        """
        if model_name not in MODEL_CONFIGS:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available models: {list(MODEL_CONFIGS.keys())}"
            )
        
        self.model_name = model_name
        self.model_config = MODEL_CONFIGS[model_name]
        self.torch_dtype = torch_dtype
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tile = tile
        self.tile_pad = tile_pad
        self.pre_pad = pre_pad
        self.upsampler: Optional[RealESRGANer] = None
        
        # Setup model cache directory in project folder
        project_root = Path(__file__).parent.parent.parent.parent
        self.model_cache_dir = project_root / "models"
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Real-ESRGAN initialized for device: {self.device}")
    
    def _get_model_path(self) -> Path:
        """Get or download the model weights."""
        model_path = self.model_cache_dir / f"{self.model_name}.pth"
        
        if not model_path.exists():
            logger.info(f"Downloading model: {self.model_name}")
            import urllib.request
            
            url = self.model_config["url"]
            try:
                urllib.request.urlretrieve(url, model_path)
                logger.info(f"Model downloaded to: {model_path}")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to download model from {url}: {e}"
                ) from e
        
        return model_path
    
    def _load_upsampler(self) -> None:
        """Load the Real-ESRGAN upsampler lazily."""
        if self.upsampler is not None:
            return
        
        logger.info(f"Loading Real-ESRGAN model: {self.model_name}")
        
        try:
            model_path = self._get_model_path()
            scale = self.model_config["scale"]
            num_block = self.model_config["num_block"]
            
            # Initialize model architecture
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=num_block,
                num_grow_ch=32,
                scale=scale,
            )
            
            # Determine GPU ID
            gpu_id = None
            if self.device == "cuda":
                gpu_id = 0 if torch.cuda.is_available() else None
            
            # Initialize upsampler
            self.upsampler = RealESRGANer(
                scale=scale,
                model_path=str(model_path),
                model=model,
                tile=self.tile,
                tile_pad=self.tile_pad,
                pre_pad=self.pre_pad,
                half=self.torch_dtype == torch.float16,
                gpu_id=gpu_id,
            )
            
            logger.info("Real-ESRGAN model loaded successfully")
            if self.tile > 0:
                logger.info(f"Tiled processing enabled: tile_size={self.tile}, tile_pad={self.tile_pad}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load Real-ESRGAN model: {e}") from e
    
    def upscale(
        self,
        input_path: str | Path,
        output_path: str | Path,
        prompt: str = "",  # Ignored, kept for compatibility
        negative_prompt: str = "",  # Ignored, kept for compatibility
        num_inference_steps: int = 50,  # Ignored, kept for compatibility
        guidance_scale: float = 9.0,  # Ignored, kept for compatibility
        noise_level: int = 20,  # Ignored, kept for compatibility
        outscale: float = 4.0,
    ) -> bool:
        """Upscale an image using Real-ESRGAN.
        
        Args:
            input_path: Path to input image
            output_path: Path to save upscaled image
            prompt: (Ignored - kept for API compatibility)
            negative_prompt: (Ignored - kept for API compatibility)
            num_inference_steps: (Ignored - kept for API compatibility)
            guidance_scale: (Ignored - kept for API compatibility)
            noise_level: (Ignored - kept for API compatibility)
            outscale: Output scale factor (default: 4.0)
        
        Returns:
            True if successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            logger.error(f"Input image not found: {input_path}")
            return False
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._load_upsampler()

            # Load image (using np.fromfile to handle non-ASCII paths)
            img_buffer = np.fromfile(str(input_path), dtype=np.uint8)
            img = cv2.imdecode(img_buffer, cv2.IMREAD_UNCHANGED)
            del img_buffer  # Free memory immediately after decode
            
            if img is None:
                logger.error(f"Failed to load image: {input_path}")
                return False
            
            original_shape = img.shape[:2]
            logger.info(f"Original input image size: {original_shape[1]}x{original_shape[0]}")
            logger.info(f"Starting upscaling with scale: {outscale}x")
            
            # Upscale
            output, _ = self.upsampler.enhance(img, outscale=outscale)
            
            # Clear GPU cache after processing to prevent VRAM accumulation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # CRITICAL FIX: Clear RealESRGANer internal tensors to prevent RAM leak
            # The upsampler stores img/output as instance variables which accumulate
            # in batch processing. Must explicitly delete them after each image.
            if self.upsampler is not None:
                if hasattr(self.upsampler, 'img'):
                    del self.upsampler.img
                if hasattr(self.upsampler, 'output'):
                    del self.upsampler.output
            
            # Save result (using imencode to handle non-ASCII paths)
            is_success, buffer = cv2.imencode(output_path.suffix, output)
            if is_success:
                buffer.tofile(str(output_path))
            else:
                logger.error(f"Failed to encode output image: {output_path}")
                del img, output  # Clean up even on failure
                gc.collect()
                return False
            
            output_shape = output.shape[:2]
            logger.info(f"✓ Upscaled image saved: {output_path}")
            logger.info(f"Output size: {output_shape[1]}x{output_shape[0]}")
            
            # Explicitly free all large arrays to prevent RAM accumulation
            # Critical for batch processing to avoid memory bloat
            del img, output, buffer
            gc.collect()  # Force garbage collection
            
            return True
            
        except Exception as e:
            logger.error(f"Upscaling failed: {e}", exc_info=True)
            return False
    
    def cleanup(self) -> None:
        """Free GPU memory."""
        if self.upsampler is not None:
            del self.upsampler
            self.upsampler = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Upsampler cleaned up")
