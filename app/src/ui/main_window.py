"""Main window for SuperImage GUI application."""

from pathlib import Path
from PySide6.QtCore import QSize, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
)


class MainWindow(QMainWindow):
    """Main application window with liquid glass theme."""

    def __init__(self):
        super().__init__()
        self.current_input_image = None
        self.settings = QSettings("SuperImage", "SuperImageApp")
        self.setup_ui()
        self.setup_processor()

    def create_themed_message_box(self, icon: QMessageBox.Icon, title: str, message: str) -> QMessageBox:
        """Create a themed QMessageBox."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # Apply dark theme styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: rgba(28, 28, 30, 0.95);
                color: #e5e5e7;
            }
            QMessageBox QLabel {
                color: #e5e5e7;
                background-color: transparent;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: rgba(0, 122, 255, 0.8);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 8px 20px;
                min-width: 70px;
                font-weight: 600;
                font-size: 13px;
            }
            QMessageBox QPushButton:hover {
                background-color: rgba(10, 132, 255, 0.9);
            }
            QMessageBox QPushButton:pressed {
                background-color: rgba(0, 112, 245, 0.9);
            }
        """)
        
        return msg_box

    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("SuperImage")
        self.setMinimumSize(QSize(1000, 700))

        # Set window icon
        self.setWindowIcon(QIcon("app/assets/app_icon.png"))

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Top bar with settings button
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Single image processing area
        single_image_area = self.create_single_image_area()
        main_layout.addWidget(single_image_area, stretch=2)

        # Single image upscale button
        single_upscale_button = self.create_single_upscale_button()
        main_layout.addWidget(single_upscale_button)

        # Multi-image selection and upscale buttons
        multi_buttons = self.create_multi_buttons()
        main_layout.addWidget(multi_buttons)

        # Multi-image list display
        image_list = self.create_image_list()
        main_layout.addWidget(image_list)

        # Progress bar
        progress_bar = self.create_progress_bar()
        main_layout.addWidget(progress_bar)

    def create_top_bar(self):
        """Create top bar with settings button."""
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(0, 0, 0, 0)

        # Model display label
        self.model_label = QLabel()
        self.model_label.setObjectName("modelLabel")
        self.update_model_display()

        # Settings button
        settings_button = QPushButton("⚙")
        settings_button.setObjectName("settingsButton")
        settings_button.setFixedSize(QSize(40, 40))
        settings_button.clicked.connect(self.open_settings)

        layout.addWidget(self.model_label)
        layout.addStretch()
        layout.addWidget(settings_button)

        return top_bar

    def create_single_image_area(self):
        """Create area for single image processing."""
        area = QWidget()
        area.setObjectName("singleImageArea")
        area.setMinimumHeight(350)  # 確保單圖區域有足夠高度不被壓縮
        layout = QHBoxLayout(area)
        layout.setSpacing(20)

        # Input area (left side)
        from src.ui.widgets.drop_area import ImageDropArea

        self.input_drop_area = ImageDropArea("Drop image here\nor click to browse")
        self.input_drop_area.setObjectName("inputDropArea")
        self.input_drop_area.image_dropped.connect(self.on_image_selected)

        # Output area (right side)
        from src.ui.widgets.image_viewer import ImageViewer

        self.output_viewer = ImageViewer("Output will appear here")
        self.output_viewer.setObjectName("outputViewer")

        layout.addWidget(self.input_drop_area, stretch=1)
        layout.addWidget(self.output_viewer, stretch=1)

        return area

    def create_single_upscale_button(self):
        """Create button for single image upscaling."""
        button = QPushButton("⬆ Upscale Image")
        button.setObjectName("upscaleButton")
        button.setMinimumHeight(50)
        button.clicked.connect(self.upscale_single_image)
        button.setEnabled(False)
        self.single_upscale_button = button
        return button

    def create_multi_buttons(self):
        """Create buttons for multi-image operations."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        select_button = QPushButton("📁 Select Multiple Images")
        select_button.setObjectName("multiImageButton")
        select_button.setMinimumHeight(50)
        select_button.clicked.connect(self.open_multi_image_dialog)

        upscale_button = QPushButton("⬆ Upscale All")
        upscale_button.setObjectName("upscaleButton")
        upscale_button.setMinimumHeight(50)
        upscale_button.clicked.connect(self.upscale_batch_images)
        upscale_button.setEnabled(False)
        self.batch_upscale_button = upscale_button

        layout.addWidget(select_button, stretch=1)
        layout.addWidget(upscale_button, stretch=1)

        return widget

    def create_image_list(self):
        """Create widget for displaying selected images."""
        from src.ui.widgets.image_list_widget import ImageListWidget

        self.image_list_widget = ImageListWidget()
        self.image_list_widget.cleared.connect(self.on_images_cleared)
        return self.image_list_widget

    def create_progress_bar(self):
        """Create progress bar for processing."""
        from src.ui.widgets.progress_widget import ProgressWidget

        self.progress_widget = ProgressWidget()
        return self.progress_widget

    def setup_processor(self):
        """Setup image processor and connect signals."""
        from src.core.image_processor import ImageProcessor

        self.processor = ImageProcessor()
        self.processor.progress.connect(self.on_progress)
        self.processor.single_finished.connect(self.on_single_finished)
        self.processor.batch_finished.connect(self.on_batch_finished)
        self.processor.error.connect(self.on_error)

    def on_image_selected(self, file_path: str):
        """Handle image selection from drop area."""
        self.current_input_image = file_path
        self.single_upscale_button.setEnabled(True)
        self.output_viewer.clear()
        self.progress_widget.reset()  # Reset progress bar when new image is selected
        
        # Add single image to the list widget
        self.image_list_widget.set_images([file_path])

    def upscale_single_image(self):
        """Upscale the currently selected single image."""
        if not self.current_input_image:
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Warning, "No Image", "Please select an image first"
            )
            msg_box.exec()
            return

        if self.processor.is_busy():
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Warning, "Busy", "Another operation is in progress. Please wait."
            )
            msg_box.exec()
            return

        # Get output directory from settings
        output_dir = self.settings.value("output_dir", str(Path.cwd() / "output"))
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Generate output path using settings output directory
        input_path = Path(self.current_input_image)
        output_path = output_dir_path / f"{input_path.stem}_upscaled{input_path.suffix}"

        self.single_upscale_button.setEnabled(False)
        self.progress_widget.reset()

        self.processor.upscale_single(self.current_input_image, str(output_path))

    def upscale_batch_images(self):
        """Upscale all images in the batch list."""
        images = self.image_list_widget.get_images()

        if not images:
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Warning, "No Images", "Please select images first"
            )
            msg_box.exec()
            return

        if self.processor.is_busy():
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Warning, "Busy", "Another operation is in progress. Please wait."
            )
            msg_box.exec()
            return

        self.batch_upscale_button.setEnabled(False)
        self.progress_widget.reset()

        self.processor.upscale_batch(images)

    def on_progress(self, value: int, status: str):
        """Handle progress updates."""
        self.progress_widget.set_progress(value, status)

    def on_single_finished(self, success: bool, output_path: str):
        """Handle single image upscaling completion."""
        self.single_upscale_button.setEnabled(True)

        if success:
            self.output_viewer.load_image(output_path)
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Information, 
                "Success", 
                f"Image upscaled successfully!\n\nSaved to:\n{output_path}"
            )
            msg_box.exec()
        else:
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Critical, "Failed", "Image upscaling failed"
            )
            msg_box.exec()

    def on_batch_finished(self, success_count: int, total: int, failed_files: list):
        """Handle batch upscaling completion."""
        self.batch_upscale_button.setEnabled(True)

        # Build message based on results
        if not failed_files:
            # All succeeded
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Information,
                "Batch Complete",
                f"Batch processing completed!\n\nSuccessfully upscaled: {success_count}/{total} images"
            )
        else:
            # Some failed
            failed_list = "\n".join([f"  • {name}" for name in failed_files])
            message = (
                f"Batch processing completed!\n\n"
                f"Successfully upscaled: {success_count}/{total} images\n"
                f"Failed: {len(failed_files)} image(s)\n\n"
                f"Failed files:\n{failed_list}"
            )
            msg_box = self.create_themed_message_box(
                QMessageBox.Icon.Warning if success_count > 0 else QMessageBox.Icon.Critical,
                "Batch Complete",
                message
            )
        msg_box.exec()

    def on_error(self, error_message: str):
        """Handle processing errors."""
        self.single_upscale_button.setEnabled(True)
        self.batch_upscale_button.setEnabled(True)
        msg_box = self.create_themed_message_box(
            QMessageBox.Icon.Critical, "Error", error_message
        )
        msg_box.exec()

    def on_images_cleared(self):
        """Handle when images are cleared from the list."""
        # Clear single image selection
        self.current_input_image = None
        self.single_upscale_button.setEnabled(False)
        self.batch_upscale_button.setEnabled(False)
        self.input_drop_area.clear()
        self.output_viewer.clear()
        self.progress_widget.reset()  # Reset progress bar when clearing all

    def update_model_display(self):
        """Update the model display label."""
        model = self.settings.value("model", "RealESRGAN_x4plus")
        model_name = "General Images" if model == "RealESRGAN_x4plus" else "Anime/Cartoon"
        self.model_label.setText(f"🎨 Model: {model_name}")

    def open_settings(self):
        """Open settings dialog."""
        from src.ui.dialogs.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self)
        if dialog.exec():
            # Update model display when settings are saved
            self.update_model_display()

    def open_multi_image_dialog(self):
        """Open multi-image selection dialog."""
        from PySide6.QtWidgets import QFileDialog

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)",
        )
        if files:
            # Clear single image mode when switching to multi-image mode
            self.current_input_image = None
            self.single_upscale_button.setEnabled(False)
            self.input_drop_area.clear()
            self.output_viewer.clear()
            self.progress_widget.reset()
            
            # Set multi-image mode
            self.image_list_widget.set_images(files)
            self.batch_upscale_button.setEnabled(True)
