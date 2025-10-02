"""Image viewer widget for displaying output."""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ImageViewer(QWidget):
    """Widget for displaying images."""

    def __init__(self, placeholder_text: str = "No image"):
        super().__init__()
        self.placeholder_text = placeholder_text
        self.current_image_path = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface."""
        self.setMinimumSize(QSize(300, 300))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label for displaying image
        self.image_label = QLabel(self.placeholder_text)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setObjectName("imageViewerLabel")
        self.image_label.setWordWrap(True)

        layout.addWidget(self.image_label)

    def load_image(self, file_path: str):
        """Load and display image."""
        self.current_image_path = file_path
        pixmap = QPixmap(file_path)

        if not pixmap.isNull():
            # Scale pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Failed to load image")

    def resizeEvent(self, event):
        """Handle resize event to rescale image."""
        super().resizeEvent(event)
        if self.current_image_path:
            self.load_image(self.current_image_path)

    def clear(self):
        """Clear the displayed image."""
        self.current_image_path = None
        self.image_label.clear()
        self.image_label.setText(self.placeholder_text)
