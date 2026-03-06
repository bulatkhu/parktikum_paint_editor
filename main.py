"""Main entry point for the Raster Graphics Editor."""

import sys

from PyQt6.QtWidgets import QApplication

from editor import EditorWindow


def main() -> None:
    """Launch the editor application."""
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()