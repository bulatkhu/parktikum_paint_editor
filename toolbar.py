"""Side toolbar with tools, colors, and brush size."""

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QColorDialog,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)


class ToolBar(QWidget):
    """Side panel with drawing tools, color picker, and brush size."""

    tool_changed = pyqtSignal(str)
    color_changed = pyqtSignal(QColor)
    size_changed = pyqtSignal(int)

    COLORS: list[tuple[str, str]] = [
        ("Red", "#FF0000"),
        ("Green", "#00AA00"),
        ("Blue", "#0000FF"),
        ("Yellow", "#FFFF00"),
        ("Orange", "#FF8800"),
        ("Violet", "#8800FF"),
        ("White", "#FFFFFF"),
        ("Black", "#000000"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(180)

        self.current_tool: str = "pencil"
        self.current_color: QColor = QColor(Qt.GlobalColor.black)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Tools section ---
        tools_label = QLabel("<b>Tools</b>")
        layout.addWidget(tools_label)

        tools_grid = QGridLayout()
        self.btn_pencil = QPushButton("✏️ Pencil")
        self.btn_eraser = QPushButton("🧹 Eraser")
        self.btn_fill = QPushButton("🪣 Fill")
        self.btn_brush = QPushButton("🖌️ Brush")

        self.btn_pencil.setCheckable(True)
        self.btn_eraser.setCheckable(True)
        self.btn_fill.setCheckable(True)
        self.btn_brush.setCheckable(True)
        self.btn_pencil.setChecked(True)

        self.btn_pencil.clicked.connect(lambda: self._select_tool("pencil"))
        self.btn_eraser.clicked.connect(lambda: self._select_tool("eraser"))
        self.btn_fill.clicked.connect(lambda: self._select_tool("fill"))
        self.btn_brush.clicked.connect(lambda: self._select_tool("brush"))

        tools_grid.addWidget(self.btn_pencil, 0, 0)
        tools_grid.addWidget(self.btn_eraser, 0, 1)
        tools_grid.addWidget(self.btn_fill, 1, 0)
        tools_grid.addWidget(self.btn_brush, 1, 1)
        layout.addLayout(tools_grid)

        # --- Size slider ---
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator1)

        size_label = QLabel("<b>Brush Size</b>")
        layout.addWidget(size_label)

        self.size_display = QLabel("3 px")
        layout.addWidget(self.size_display)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(50)
        self.slider.setValue(3)
        self.slider.valueChanged.connect(self._on_size_changed)
        layout.addWidget(self.slider)

        # --- Colors section ---
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator2)

        colors_label = QLabel("<b>Colors</b>")
        layout.addWidget(colors_label)

        color_grid = QGridLayout()
        self.color_buttons: list[QPushButton] = []

        for i, (name, hex_color) in enumerate(self.COLORS):
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setToolTip(name)
            border = "1px solid #999" if hex_color != "#FFFFFF" else "1px solid #CCC"
            btn.setStyleSheet(
                f"background-color: {hex_color}; border: {border}; border-radius: 4px;"
            )
            btn.clicked.connect(lambda checked, c=hex_color: self._select_color(c))
            color_grid.addWidget(btn, i // 4, i % 4)
            self.color_buttons.append(btn)

        layout.addLayout(color_grid)

        # Current color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(160, 24)
        self._update_color_preview()
        layout.addWidget(self.color_preview)

        # "Other" button for custom color
        btn_other = QPushButton("🎨 Other...")
        btn_other.clicked.connect(self._pick_custom_color)
        layout.addWidget(btn_other)

        layout.addStretch()

    def _select_tool(self, tool: str) -> None:
        """Handle tool selection."""
        self.current_tool = tool
        self.btn_pencil.setChecked(tool == "pencil")
        self.btn_eraser.setChecked(tool == "eraser")
        self.btn_fill.setChecked(tool == "fill")
        self.btn_brush.setChecked(tool == "brush")
        self.tool_changed.emit(tool)

    def _select_color(self, hex_color: str) -> None:
        """Handle color button click."""
        self.current_color = QColor(hex_color)
        self._update_color_preview()
        self.color_changed.emit(self.current_color)

    def _pick_custom_color(self) -> None:
        """Open color dialog for custom color."""
        color = QColorDialog.getColor(self.current_color, self, "Pick a Color")
        if color.isValid():
            self.current_color = color
            self._update_color_preview()
            self.color_changed.emit(color)

    def _on_size_changed(self, value: int) -> None:
        """Handle slider change."""
        self.size_display.setText(f"{value} px")
        self.size_changed.emit(value)

    def _update_color_preview(self) -> None:
        """Update the color preview label."""
        self.color_preview.setStyleSheet(
            f"background-color: {self.current_color.name()}; "
            f"border: 1px solid #999; border-radius: 4px;"
        )