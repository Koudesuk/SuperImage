"""Progress bar widget for tracking processing."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel


class ProgressWidget(QWidget):
    """Widget for displaying processing progress."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(30)

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

    def set_progress(self, value: int, status: str = ""):
        """Set progress value and optional status text."""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)

    def reset(self):
        """Reset progress to initial state."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
