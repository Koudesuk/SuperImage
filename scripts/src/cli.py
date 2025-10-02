"""Command-line interface for SuperImage toolkit."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Handle both direct script execution and module import
if __name__ == "__main__" and __package__ is None:
    # Add parent directory to path for direct execution
    script_dir = Path(__file__).resolve().parent
    parent_dir = script_dir.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from scripts.src.models.real_esrgan import RealESRGANUpscaler
else:
    from .models.real_esrgan import RealESRGANUpscaler


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )


def upscale_command(args: argparse.Namespace) -> int:
    """Handle the upscale command."""
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        return 1
    
    if not input_path.is_file():
        print(f"Error: '{input_path}' is not a file", file=sys.stderr)
        return 1
    
    print(f"Upscaling: {input_path} -> {output_path}")
    print(f"Using model: {args.model}")
    
    upscaler = RealESRGANUpscaler(model_name=args.model)
    
    try:
        success = upscaler.upscale(
            input_path=input_path,
            output_path=output_path,
            prompt=args.prompt,
            negative_prompt=args.negative_prompt,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance,
            noise_level=args.noise_level,
        )
        
        if success:
            print(f"✓ Successfully upscaled to: {output_path}")
            return 0
        else:
            print("✗ Upscaling failed", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\\n✗ Upscaling cancelled", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    finally:
        upscaler.cleanup()


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="superimage",
        description="Image super-resolution using Real-ESRGAN",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    upscale_parser = subparsers.add_parser(
        "upscale",
        help="Upscale an image using Real-ESRGAN",
    )
    
    upscale_parser.add_argument(
        "input",
        type=str,
        help="Input image path",
    )
    
    upscale_parser.add_argument(
        "output",
        type=str,
        help="Output image path",
    )
    
    upscale_parser.add_argument(
        "--prompt",
        type=str,
        default="high quality, detailed, sharp, 4k",
        help="Text prompt to guide upscaling (default: %(default)s)",
    )
    
    upscale_parser.add_argument(
        "--negative-prompt",
        type=str,
        default="blurry, low quality, pixelated, artifacts",
        help="Negative prompt to avoid unwanted features (default: %(default)s)",
    )
    
    upscale_parser.add_argument(
        "--steps",
        type=int,
        default=50,
        help="Number of inference steps (default: %(default)s)",
    )
    
    upscale_parser.add_argument(
        "--guidance",
        type=float,
        default=9.0,
        help="Guidance scale (default: %(default)s)",
    )
    
    upscale_parser.add_argument(
        "--noise-level",
        type=int,
        default=20,
        help="Noise level for upscaling (default: %(default)s)",
    )
    
    upscale_parser.add_argument(
        "--model",
        type=str,
        default="RealESRGAN_x4plus",
        choices=["RealESRGAN_x4plus", "RealESRGAN_x4plus_anime_6B"],
        help="Model to use: RealESRGAN_x4plus (general) or RealESRGAN_x4plus_anime_6B (anime) (default: %(default)s)",
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if args.command == "upscale":
        return upscale_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
