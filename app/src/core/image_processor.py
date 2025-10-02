"""Image processor for handling upscaling operations."""

import sys
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal, QThread, QSettings

# Add project root to path for importing
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.src.models.real_esrgan import RealESRGANUpscaler  # noqa: E402


class UpscaleWorker(QThread):
    """Worker thread for running upscale operations."""

    progress = Signal(int, str)
    finished = Signal(bool, str)
    error = Signal(str)

    def __init__(
        self,
        input_path: str,
        output_path: str,
        model_name: str,
        tile: int,
        tile_pad: int,
        pre_pad: int,
        outscale: float,
    ):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.model_name = model_name
        self.tile = tile
        self.tile_pad = tile_pad
        self.pre_pad = pre_pad
        self.outscale = outscale

    def run(self):
        """Run the upscaling operation."""
        try:
            self.progress.emit(10, f"Initializing {self.model_name}...")

            upscaler = RealESRGANUpscaler(
                model_name=self.model_name,
                tile=self.tile,
                tile_pad=self.tile_pad,
                pre_pad=self.pre_pad,
            )

            self.progress.emit(30, "Loading model...")

            success = upscaler.upscale(
                input_path=self.input_path,
                output_path=self.output_path,
                outscale=self.outscale,
            )

            upscaler.cleanup()

            if success:
                self.progress.emit(100, "Upscaling completed!")
                self.finished.emit(True, self.output_path)
            else:
                self.error.emit("Upscaling failed")
                self.finished.emit(False, "")

        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
            self.finished.emit(False, "")


class BatchUpscaleWorker(QThread):
    """Worker thread for batch upscaling operations."""

    progress = Signal(int, str)
    finished = Signal(int, int)
    error = Signal(str)

    def __init__(
        self,
        input_paths: list[str],
        output_dir: str,
        model_name: str,
        tile: int,
        tile_pad: int,
        pre_pad: int,
        outscale: float,
    ):
        super().__init__()
        self.input_paths = input_paths
        self.output_dir = output_dir
        self.model_name = model_name
        self.tile = tile
        self.tile_pad = tile_pad
        self.pre_pad = pre_pad
        self.outscale = outscale

    def run(self):
        """Run batch upscaling operations."""
        try:
            total = len(self.input_paths)
            success_count = 0

            self.progress.emit(0, f"Initializing {self.model_name}...")

            upscaler = RealESRGANUpscaler(
                model_name=self.model_name,
                tile=self.tile,
                tile_pad=self.tile_pad,
                pre_pad=self.pre_pad,
            )

            output_dir_path = Path(self.output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)

            for idx, input_path in enumerate(self.input_paths):
                input_file = Path(input_path)
                output_file = output_dir_path / f"{input_file.stem}_upscaled{input_file.suffix}"

                current_progress = int((idx / total) * 100)
                self.progress.emit(
                    current_progress,
                    f"Processing {idx + 1}/{total}: {input_file.name}",
                )

                success = upscaler.upscale(
                    input_path=input_path,
                    output_path=str(output_file),
                    outscale=self.outscale,
                )

                if success:
                    success_count += 1

            upscaler.cleanup()

            self.progress.emit(100, "Batch processing completed!")
            self.finished.emit(success_count, total)

        except Exception as e:
            self.error.emit(f"Batch processing error: {str(e)}")
            self.finished.emit(0, len(self.input_paths))


class ImageProcessor(QObject):
    """Manager for image upscaling operations."""

    progress = Signal(int, str)
    single_finished = Signal(bool, str)
    batch_finished = Signal(int, int)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("SuperImage", "SuperImageApp")
        self.worker: Optional[QThread] = None

    def get_settings(self) -> dict:
        """Get current settings."""
        return {
            "model": self.settings.value("model", "RealESRGAN_x4plus"),
            "output_dir": self.settings.value("output_dir", str(Path.cwd() / "output")),
            "tile": int(self.settings.value("tile", 400)),
            "tile_pad": int(self.settings.value("tile_pad", 10)),
            "pre_pad": int(self.settings.value("pre_pad", 0)),
            "outscale": float(self.settings.value("outscale", 4.0)),
        }

    def upscale_single(self, input_path: str, output_path: str):
        """Upscale a single image."""
        if self.worker and self.worker.isRunning():
            self.error.emit("Another operation is already running")
            return

        settings = self.get_settings()

        self.worker = UpscaleWorker(
            input_path=input_path,
            output_path=output_path,
            model_name=settings["model"],
            tile=settings["tile"],
            tile_pad=settings["tile_pad"],
            pre_pad=settings["pre_pad"],
            outscale=settings["outscale"],
        )

        self.worker.progress.connect(self.progress.emit)
        self.worker.finished.connect(self.single_finished.emit)
        self.worker.error.connect(self.error.emit)

        self.worker.start()

    def upscale_batch(self, input_paths: list[str]):
        """Upscale multiple images."""
        if self.worker and self.worker.isRunning():
            self.error.emit("Another operation is already running")
            return

        settings = self.get_settings()

        self.worker = BatchUpscaleWorker(
            input_paths=input_paths,
            output_dir=settings["output_dir"],
            model_name=settings["model"],
            tile=settings["tile"],
            tile_pad=settings["tile_pad"],
            pre_pad=settings["pre_pad"],
            outscale=settings["outscale"],
        )

        self.worker.progress.connect(self.progress.emit)
        self.worker.finished.connect(self.batch_finished.emit)
        self.worker.error.connect(self.error.emit)

        self.worker.start()

    def is_busy(self) -> bool:
        """Check if processor is currently running."""
        return self.worker is not None and self.worker.isRunning()
