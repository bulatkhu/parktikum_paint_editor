"""Main editor window combining canvas, toolbar, and menus."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QImage, QPainter
from PyQt6.QtWidgets import (
    QMainWindow,
    QHBoxLayout,
    QWidget,
    QScrollArea,
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QSpinBox,
    QDialogButtonBox,
)

from canvas import Canvas
from toolbar import ToolBar


class NewImageDialog(QDialog):
    """Dialog to set dimensions for a new image."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Image")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Width (px):"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(1280)
        layout.addWidget(self.width_spin)

        layout.addWidget(QLabel("Height (px):"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(720)
        layout.addWidget(self.height_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_size(self) -> tuple[int, int]:
        """Return the chosen (width, height)."""
        return self.width_spin.value(), self.height_spin.value()


class EditorWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Paint Editor")
        self.setMinimumSize(800, 600)

        # --- Canvas in scroll area ---
        self.canvas = Canvas()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Toolbar ---
        self.toolbar = ToolBar()
        self.toolbar.tool_changed.connect(self.canvas.set_tool)
        self.toolbar.color_changed.connect(self.canvas.set_color)
        self.toolbar.size_changed.connect(self.canvas.set_pen_size)

        # --- Layout ---
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.scroll_area, stretch=1)
        self.setCentralWidget(central)

        # --- Menu bar ---
        self._create_menus()

    def _create_menus(self) -> None:
        """Set up File menu."""
        menu_bar = self.menuBar()
        if menu_bar is None:
            return

        file_menu = menu_bar.addMenu("File")
        if file_menu is None:
            return

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_image)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_image)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_image)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _new_image(self) -> None:
        """Create a new blank image."""
        dialog = NewImageDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            w, h = dialog.get_size()
            self.canvas.new_image(w, h)

    def _open_image(self) -> None:
        """Open an image file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg);;All Files (*)",
        )
        if not path:
            return

        image = QImage(path)
        if image.isNull():
            QMessageBox.warning(self, "Error", "Could not open image.")
            return

        # Handle alpha channel
        if image.hasAlphaChannel():
            result = QMessageBox.question(
                self,
                "Alpha Channel Detected",
                "This image has an alpha channel (transparency).\n\n"
                "Keep transparency? (No = flatten to white background)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if result == QMessageBox.StandardButton.Yes:
                self.canvas.image = image.convertToFormat(QImage.Format.Format_ARGB32)
            else:
                # Flatten: paint image onto white background
                flat = QImage(image.size(), QImage.Format.Format_ARGB32)
                flat.fill(Qt.GlobalColor.white)
                painter = QPainter(flat)
                painter.drawImage(0, 0, image)
                painter.end()
                self.canvas.image = flat
        else:
            self.canvas.image = image.convertToFormat(QImage.Format.Format_ARGB32)
        self.canvas.zoom_factor = 1.0
        self.canvas._update_size()

    def _save_image(self) -> None:
        """Save the current image."""
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "untitled.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg)",
        )
        if not path:
            return

        # Ensure correct extension
        if "JPEG" in selected_filter and not (path.endswith(".jpg") or path.endswith(".jpeg")):
            path += ".jpg"
        elif "PNG" in selected_filter and not path.endswith(".png"):
            path += ".png"

        if not self.canvas.image.save(path):
            QMessageBox.warning(self, "Error", "Could not save image.")