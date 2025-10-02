"""SuperImage GUI Application Entry Point."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Set high DPI scaling
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("SuperImage")
    app.setOrganizationName("SuperImage")
    app.setApplicationDisplayName("SuperImage - Image Upscaler")

    # Load and apply stylesheet
    style_path = Path(__file__).parent / "src" / "ui" / "styles" / "liquid_glass.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # Create and show main window
    from src.ui.main_window import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
