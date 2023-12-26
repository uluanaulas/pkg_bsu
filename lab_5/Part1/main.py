import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QToolBar
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import numpy as np
import random as rand
from line_clipping import *

# function to perform the line clipping and render the results on the matplotlib figure
def clip_and_render(lines, viewport, ax):
    for line in lines:
        # clip the line
        clipped_line = clip_line(line, viewport)
        ax.plot([line.x1, line.x2], [line.y1, line.y2], color='gray')

        if clipped_line:
            # generate a random color for the line
            color = (rand.uniform(0, 0.8), rand.uniform(0, 0.8), rand.uniform(0, 0.8))
            ax.plot([clipped_line.x1, clipped_line.x2], [clipped_line.y1, clipped_line.y2], color=color)

    # render the viewport rectangle
    ax.add_patch(Rectangle((viewport.xmin, viewport.ymin), viewport.xmax - viewport.xmin, viewport.ymax - viewport.ymin, fill=None, linewidth=3, color='r'))

class CustomCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

        self.rescale([], Viewport(0,0,10,10))

    def rescale(self, lines : list[Line], viewport : Viewport):
        if lines:
            lines_x = [line.x1 for line in lines]
            lines_x.extend([line.x2 for line in lines])
            lines_y = [line.y1 for line in lines]
            lines_y.extend([line.y2 for line in lines])

            self.x_min, self.x_max = min(viewport.xmin, min(lines_x)), max(viewport.xmax, max(lines_x))
            self.y_min, self.y_max = min(viewport.ymin, min(lines_y)), max(viewport.ymax, max(lines_y))
        else:
            self.x_min, self.x_max = viewport.xmin, viewport.xmax
            self.y_min, self.y_max = viewport.ymin, viewport.ymax

        self.axes.grid(True, "both", "both")
        self.axes.set_ylim(self.y_min - 1, self.y_max + 1)
        self.axes.set_xlim(self.x_min - 1, self.x_max + 1)

# define the main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cohen-Sutherland Line Clipping Algorithm')
        self.setGeometry(100, 100, 800, 600)

        # create the matplotlib figure and canvas
        self.canvas = CustomCanvas(self, width=5, height=4, dpi=100)

        # create the button
        self.button = QPushButton('Open File')
        self.button.clicked.connect(self.open_file)

        # create the toolbar and add the button to it
        toolbar = QToolBar()
        toolbar.addWidget(self.button)

        # add the figure canvas and toolbar to the main window
        self.addToolBar(toolbar)
        self.setCentralWidget(self.canvas)
        
    # function to read the file and return a list of lines and a viewport object
    def read_file(self, filename):
        with open(filename, 'r') as f:
            n = int(f.readline())
            lines = []
            for i in range(n):
                x1, y1, x2, y2 = [float(x) for x in f.readline().split()]
                lines.append(Line(x1, y1, x2, y2))
            xmin, ymin, xmax, ymax = [float(x) for x in f.readline().split()]
            viewport = Viewport(xmin, ymin, xmax, ymax)
        return lines, viewport

    # function to open the file dialog and read the selected file
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '.', 'Line Files (*.line)')
        if filename:
            lines, viewport = self.read_file(filename)
            
            self.canvas.axes.clear()
            self.canvas.rescale(lines, viewport)
            clip_and_render(lines, viewport, self.canvas.axes)
            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())