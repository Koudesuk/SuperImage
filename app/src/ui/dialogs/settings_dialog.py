"""Settings dialog for model and output directory selection."""

from pathlib import Path
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QDialogButtonBox,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QScrollArea,
    QWidget,
)


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("SuperImage", "SuperImageApp")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(650)
        self.setObjectName("settingsDialog")

        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("settingsScrollArea")

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(20)

        # Model selection
        model_layout = QVBoxLayout()
        model_label = QLabel("Select Model:")
        model_label.setObjectName("settingLabel")

        self.model_combo = QComboBox()
        self.model_combo.setObjectName("modelComboBox")
        self.model_combo.addItem("RealESRGAN_x4plus (General Images)", "RealESRGAN_x4plus")
        self.model_combo.addItem(
            "RealESRGAN_x4plus_anime_6B (Anime/Cartoon)", "RealESRGAN_x4plus_anime_6B"
        )

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)

        # Output directory selection
        output_layout = QVBoxLayout()
        output_label = QLabel("Output Directory:")
        output_label.setObjectName("settingLabel")

        dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setObjectName("outputDirEdit")
        self.output_dir_edit.setReadOnly(True)

        browse_button = QPushButton("Browse...")
        browse_button.setObjectName("browseButton")
        browse_button.clicked.connect(self.browse_output_dir)

        dir_layout.addWidget(self.output_dir_edit, stretch=1)
        dir_layout.addWidget(browse_button)

        output_layout.addWidget(output_label)
        output_layout.addLayout(dir_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.setObjectName("dialogButtonBox")
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)

        # Advanced settings group
        advanced_group = self.create_advanced_settings()

        # Add all to main layout
        layout.addLayout(model_layout)
        layout.addLayout(output_layout)
        layout.addWidget(advanced_group)
        layout.addStretch()

        scroll_area.setWidget(scroll_widget)

        # Main dialog layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(button_box)

    def load_settings(self):
        """Load saved settings."""
        # Load model selection
        model = self.settings.value("model", "RealESRGAN_x4plus")
        index = self.model_combo.findData(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)

        # Load output directory
        output_dir = self.settings.value("output_dir", str(Path.cwd() / "output"))
        self.output_dir_edit.setText(output_dir)

        # Load advanced settings
        self.tile_spin.setValue(int(self.settings.value("tile", 400)))
        self.tile_pad_spin.setValue(int(self.settings.value("tile_pad", 10)))
        self.pre_pad_spin.setValue(int(self.settings.value("pre_pad", 0)))
        self.outscale_spin.setValue(float(self.settings.value("outscale", 4.0)))

    def save_and_accept(self):
        """Save settings and close dialog."""
        self.settings.setValue("model", self.model_combo.currentData())
        self.settings.setValue("output_dir", self.output_dir_edit.text())
        self.settings.setValue("tile", self.tile_spin.value())
        self.settings.setValue("tile_pad", self.tile_pad_spin.value())
        self.settings.setValue("pre_pad", self.pre_pad_spin.value())
        self.settings.setValue("outscale", self.outscale_spin.value())
        self.accept()

    def browse_output_dir(self):
        """Open directory browser."""
        current_dir = self.output_dir_edit.text() or str(Path.cwd())
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", current_dir
        )
        if directory:
            self.output_dir_edit.setText(directory)

    def create_advanced_settings(self):
        """Create advanced settings group."""
        group = QGroupBox("Advanced Settings")
        group.setObjectName("advancedGroup")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)

        # Tile size
        tile_layout = QHBoxLayout()
        tile_label = QLabel("Tile Size:")
        tile_label.setObjectName("settingLabel")
        self.tile_spin = QSpinBox()
        self.tile_spin.setObjectName("spinBox")
        self.tile_spin.setRange(0, 1024)
        self.tile_spin.setValue(400)
        self.tile_spin.setSuffix(" px")
        self.tile_spin.setToolTip("Tile size for processing (0 = no tiling, larger = more VRAM)")
        tile_layout.addWidget(tile_label)
        tile_layout.addWidget(self.tile_spin, stretch=1)

        # Tile padding
        tile_pad_layout = QHBoxLayout()
        tile_pad_label = QLabel("Tile Padding:")
        tile_pad_label.setObjectName("settingLabel")
        self.tile_pad_spin = QSpinBox()
        self.tile_pad_spin.setObjectName("spinBox")
        self.tile_pad_spin.setRange(0, 50)
        self.tile_pad_spin.setValue(10)
        self.tile_pad_spin.setSuffix(" px")
        self.tile_pad_spin.setToolTip("Padding for tiles to reduce seams")
        tile_pad_layout.addWidget(tile_pad_label)
        tile_pad_layout.addWidget(self.tile_pad_spin, stretch=1)

        # Pre-padding
        pre_pad_layout = QHBoxLayout()
        pre_pad_label = QLabel("Pre-Padding:")
        pre_pad_label.setObjectName("settingLabel")
        self.pre_pad_spin = QSpinBox()
        self.pre_pad_spin.setObjectName("spinBox")
        self.pre_pad_spin.setRange(0, 50)
        self.pre_pad_spin.setValue(0)
        self.pre_pad_spin.setSuffix(" px")
        self.pre_pad_spin.setToolTip("Pre-padding size before processing")
        pre_pad_layout.addWidget(pre_pad_label)
        pre_pad_layout.addWidget(self.pre_pad_spin, stretch=1)

        # Output scale
        outscale_layout = QHBoxLayout()
        outscale_label = QLabel("Output Scale:")
        outscale_label.setObjectName("settingLabel")
        self.outscale_spin = QDoubleSpinBox()
        self.outscale_spin.setObjectName("doubleSpinBox")
        self.outscale_spin.setRange(1.0, 8.0)
        self.outscale_spin.setValue(4.0)
        self.outscale_spin.setSingleStep(0.5)
        self.outscale_spin.setSuffix("x")
        self.outscale_spin.setToolTip("Output upscale factor")
        outscale_layout.addWidget(outscale_label)
        outscale_layout.addWidget(self.outscale_spin, stretch=1)

        # Add all to group
        group_layout.addLayout(tile_layout)
        group_layout.addLayout(tile_pad_layout)
        group_layout.addLayout(pre_pad_layout)
        group_layout.addLayout(outscale_layout)

        return group

    def get_model(self) -> str:
        """Get selected model."""
        return self.model_combo.currentData()

    def get_output_dir(self) -> str:
        """Get selected output directory."""
        return self.output_dir_edit.text()
