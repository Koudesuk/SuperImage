"""Drag and drop image area widget."""

from pathlib import Path
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QFileDialog


class ImageDropArea(QWidget):
    """Widget for drag-and-drop image upload."""

    image_dropped = Signal(str)

    def __init__(self, placeholder_text: str = "Drop image here"):
        super().__init__()
        self.placeholder_text = placeholder_text
        self.current_image_path = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface."""
        self.setAcceptDrops(True)
        self.setMinimumSize(QSize(300, 300))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label for displaying image or placeholder
        self.image_label = QLabel(self.placeholder_text)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setObjectName("dropAreaLabel")
        self.image_label.setWordWrap(True)

        layout.addWidget(self.image_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self.is_valid_image(file_path):
                self.load_image(file_path)
                self.image_dropped.emit(file_path)

    def mousePressEvent(self, event):
        """Handle mouse click to open file dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_file_dialog()

    def open_file_dialog(self):
        """Open file dialog to select image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)",
        )
        if file_path:
            self.load_image(file_path)
            self.image_dropped.emit(file_path)

    def is_valid_image(self, file_path: str) -> bool:
        """Check if file is a valid image."""
        valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        return Path(file_path).suffix.lower() in valid_extensions

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
