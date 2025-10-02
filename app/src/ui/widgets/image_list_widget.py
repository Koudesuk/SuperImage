"""Widget for displaying list of selected images with paths."""

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
)


class ImageListWidget(QWidget):
    """Widget for displaying selected image files with their paths."""

    images_changed = Signal(list)
    cleared = Signal()

    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header with title and clear button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Selected Images")
        title_label.setObjectName("imageListTitle")

        self.count_label = QLabel("(0 images)")
        self.count_label.setObjectName("imageListCount")

        self.clear_button = QPushButton("Clear All")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_all)
        self.clear_button.setVisible(False)

        header_layout.addWidget(title_label)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        header_layout.addWidget(self.clear_button)

        # List widget for displaying images
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("imageListWidget")
        self.list_widget.setMinimumHeight(150)
        self.list_widget.setMaximumHeight(250)

        layout.addLayout(header_layout)
        layout.addWidget(self.list_widget)

    def add_images(self, file_paths: list[str]):
        """Add images to the list."""
        self.image_paths.extend(file_paths)
        self._update_list()
        self.images_changed.emit(self.image_paths)

    def set_images(self, file_paths: list[str]):
        """Set images, replacing current list."""
        self.image_paths = file_paths
        self._update_list()
        self.images_changed.emit(self.image_paths)

    def clear_all(self):
        """Clear all images from the list."""
        self.image_paths.clear()
        self._update_list()
        self.images_changed.emit(self.image_paths)
        self.cleared.emit()

    def _update_list(self):
        """Update the list widget display."""
        self.list_widget.clear()

        for file_path in self.image_paths:
            path = Path(file_path)
            item = QListWidgetItem()

            # Create display text with filename and path
            filename = path.name
            parent_dir = str(path.parent)

            item_text = f"{filename}\n{parent_dir}"
            item.setText(item_text)
            item.setToolTip(file_path)

            self.list_widget.addItem(item)

        # Update count label
        count = len(self.image_paths)
        self.count_label.setText(f"({count} image{'s' if count != 1 else ''})")

        # Show/hide clear button
        self.clear_button.setVisible(count > 0)

    def get_images(self) -> list[str]:
        """Get list of image paths."""
        return self.image_paths.copy()
