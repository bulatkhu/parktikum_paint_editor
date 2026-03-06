"""Canvas widget for drawing."""

from collections import deque

from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import (
    QImage,
    QPainter,
    QPen,
    QColor,
    QWheelEvent,
    QMouseEvent,
    QPaintEvent,
    QRadialGradient,
    QBrush,
)
from PyQt6.QtWidgets import QWidget


class Canvas(QWidget):
    """Main drawing canvas that holds a QImage and supports painting tools."""

    def __init__(self, width: int = 1280, height: int = 720, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # The actual image we draw on (ARGB32 for alpha channel support)
        self.image: QImage = QImage(width, height, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.white)

        # Drawing state
        self.drawing: bool = False
        self.last_point: QPoint = QPoint()

        # Tool settings
        self.pen_color: QColor = QColor(Qt.GlobalColor.black)
        self.pen_size: int = 3
        self.current_tool: str = "pencil"  # "pencil", "eraser", "fill", or "brush"

        # Zoom
        self.zoom_factor: float = 1.0

        # Update widget size to match image
        self._update_size()

    def _update_size(self) -> None:
        """Resize widget to match image * zoom."""
        w = int(self.image.width() * self.zoom_factor)
        h = int(self.image.height() * self.zoom_factor)
        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)
        self.update()

    def new_image(self, width: int, height: int) -> None:
        """Create a new blank white image."""
        self.image = QImage(width, height, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.white)
        self._update_size()

    def set_tool(self, tool: str) -> None:
        """Set current tool ('pencil' or 'eraser')."""
        self.current_tool = tool

    def set_color(self, color: QColor) -> None:
        """Set pen color."""
        self.pen_color = color

    def set_pen_size(self, size: int) -> None:
        """Set pen size in pixels."""
        self.pen_size = size

    def _get_drawing_color(self) -> QColor:
        """Return the color to use based on current tool."""
        if self.current_tool == "eraser":
            return QColor(Qt.GlobalColor.white)
        return self.pen_color

    def _map_to_image(self, pos: QPoint) -> QPoint:
        """Map widget coordinates to image coordinates (accounting for zoom)."""
        x = int(pos.x() / self.zoom_factor)
        y = int(pos.y() / self.zoom_factor)
        return QPoint(x, y)

    # --- Paint event ---

    def paintEvent(self, event: QPaintEvent | None) -> None:
        """Draw the image onto the widget."""
        painter = QPainter(self)
        # Draw checkerboard behind transparent areas
        self._draw_checkerboard(painter)
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.drawImage(0, 0, self.image)
        painter.end()

    def _draw_checkerboard(self, painter: QPainter) -> None:
        """Draw a checkerboard pattern to indicate transparency."""
        cell = 8
        w = int(self.image.width() * self.zoom_factor)
        h = int(self.image.height() * self.zoom_factor)
        light = QColor(220, 220, 220)
        dark = QColor(180, 180, 180)
        for y in range(0, h, cell):
            for x in range(0, w, cell):
                color = light if (x // cell + y // cell) % 2 == 0 else dark
                painter.fillRect(x, y, cell, cell, color)

    # --- Mouse events for drawing ---

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        """Start drawing or perform fill."""
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            img_pos = self._map_to_image(event.pos())

            if self.current_tool == "fill":
                self._flood_fill(img_pos)
                self.update()
            else:
                self.drawing = True
                self.last_point = img_pos
                # For brush, draw a single dab on click
                if self.current_tool == "brush":
                    self._draw_brush_dab(img_pos)
                    self.update()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        """Draw line / brush stroke from last point to current point."""
        if event is not None and self.drawing:
            current_point = self._map_to_image(event.pos())

            if self.current_tool == "brush":
                self._draw_brush_dab(current_point)
            else:
                painter = QPainter(self.image)
                pen = QPen(
                    self._get_drawing_color(),
                    self.pen_size,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
                painter.setPen(pen)
                painter.drawLine(self.last_point, current_point)
                painter.end()

            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        """Stop drawing."""
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    # --- Brush tool (soft / semi-transparent radial dab) ---

    def _draw_brush_dab(self, center: QPoint) -> None:
        """Draw a single soft brush dab at the given image coordinate."""
        painter = QPainter(self.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self._get_drawing_color()
        radius = self.pen_size

        # Radial gradient: opaque center fading to transparent edge
        center_f = QPointF(float(center.x()), float(center.y()))
        gradient = QRadialGradient(center_f, float(radius))
        inner = QColor(color)
        inner.setAlpha(160)
        outer = QColor(color)
        outer.setAlpha(0)
        gradient.setColorAt(0.0, inner)
        gradient.setColorAt(1.0, outer)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(center_f, float(radius), float(radius))
        painter.end()

    # --- Flood fill (BFS) ---

    def _flood_fill(self, start: QPoint) -> None:
        """Fill a contiguous region of the same color with the current color."""
        x0, y0 = start.x(), start.y()
        w, h = self.image.width(), self.image.height()
        if x0 < 0 or x0 >= w or y0 < 0 or y0 >= h:
            return

        target_rgba = self.image.pixelColor(x0, y0).rgba()
        fill_color = self._get_drawing_color()
        fill_rgba = fill_color.rgba()

        if target_rgba == fill_rgba:
            return  # already same color, nothing to do

        queue: deque[tuple[int, int]] = deque()
        queue.append((x0, y0))
        visited: set[tuple[int, int]] = {(x0, y0)}

        while queue:
            cx, cy = queue.popleft()
            self.image.setPixelColor(cx, cy, fill_color)

            for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    if self.image.pixelColor(nx, ny).rgba() == target_rgba:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

    # --- Zoom ---

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        """Zoom in/out with scroll wheel."""
        if event is None:
            return
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_factor = min(self.zoom_factor + 0.1, 4.0)
        else:
            self.zoom_factor = max(self.zoom_factor - 0.1, 0.25)
        self._update_size()