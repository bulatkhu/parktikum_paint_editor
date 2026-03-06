# Raster Graphics Editor

A simple raster graphics editor built with PyQt6. This application allows users to draw, edit, and save images using a variety of tools, colors, and brush sizes.

---

## Table of Contents

1. Features
2. Installation
3. Usage
4. Project Structure
5. Modules
6. Contributing
7. License

---

## Features

- **Drawing Tools**: Pencil, Eraser, Brush, and Fill.
- **Color Picker**: Predefined colors and a custom color picker.
- **Brush Size**: Adjustable brush size from 1px to 50px.
- **Zoom**: Zoom in and out using the mouse wheel.
- **File Operations**: Create new images, open existing ones, and save your work.
- **Transparency Support**: Handles images with alpha channels and allows flattening transparency.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bulatkhu/parktikum_paint_editor.git
   cd parktikum_paint_editor
   ```
   
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install PyQt6
   ```

4. To verify whether everything is typed properly:
   ```bash
   mypy --strict .
   ```

## Usage: 

1. Run the application:
   ```bash
   python main.py 
   ```

2. Use the toolbar on the left to select tools, colors, and brush sizes.

3. Use the menu bar to create new images, open existing ones, or save your work.

## Project Structure
```md
.
├── canvas.py       # Canvas widget for drawing
├── editor.py       # Main editor window combining canvas, toolbar, and menus
├── main.py         # Entry point for the application
├── toolbar.py      # Side toolbar with tools, colors, and brush size
├── .gitignore      # Git ignore file
├── venv/           # Virtual environment (ignored by Git)
└── .mypy_cache/    # mypy type-checking cache (ignored by Git)
```

## Modules
1. canvas.py
The Canvas class provides the main drawing area. It supports tools like pencil, eraser, brush, and fill, along with zoom functionality.

2. toolbar.py
The ToolBar class provides a side panel for selecting tools, colors, and brush sizes. It emits signals to communicate with the canvas.

3. editor.py
The EditorWindow class is the main application window. It combines the canvas and toolbar, and provides menu options for file operations.

4. main.py
The main function initializes the application and launches the editor window.