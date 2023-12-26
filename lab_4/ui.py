import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox
import numpy as np
from raster import *
from time import time

class Line():
    def __init__(self, start_x, start_y, end_x, end_y, color):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color

class ZoomableCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.mpl_connect("scroll_event", self.zoom)

        self.reset()

    def reset(self):
        self.zoom_factor = 1.05
        self.base_scale = 1
        self.x_min, self.x_max = -40, 40
        self.y_min, self.y_max = -40, 40

        self.axes.grid(True, "both", "both")
        self.calculate_zoom(0,0,1)

    def calculate_zoom(self, xdata, ydata, scale_factor):
        self.x_min = xdata - (xdata - self.x_min) * scale_factor
        self.x_max = xdata + (self.x_max - xdata) * scale_factor
        self.y_min = ydata - (ydata - self.y_min) * scale_factor
        self.y_max = ydata + (self.y_max - ydata) * scale_factor

        self.axes.set_xlim(self.x_min, self.x_max)
        self.axes.set_ylim(self.y_min, self.y_max)
        self.draw()

    def zoom(self, event):
        if event.button == 'up':
            scale_factor = 1 / self.zoom_factor
        elif event.button == 'down':
            scale_factor = self.zoom_factor
        else:
            return

        xdata = event.xdata
        ydata = event.ydata
        self.calculate_zoom(xdata, ydata, scale_factor)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coordinate Plane")

        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        self.canvas = ZoomableCanvas(self, width=5, height=4, dpi=100)
        self.layout.addWidget(self.canvas)

        self.rasterize_dropdown = QComboBox()
        self.rasterize_dropdown.addItem("Naive")
        self.rasterize_dropdown.addItem("Digital Differential Analyzer (DDA)")
        self.rasterize_dropdown.addItem("Bresenham's Line Algorithm")
        self.rasterize_dropdown.addItem("Bresenham's Circle Algorithm")
        self.layout.addWidget(self.rasterize_dropdown)

        self.draw_button = QPushButton("Draw")
        self.clear_button = QPushButton("Clear")
        self.layout.addWidget(self.draw_button)
        self.layout.addWidget(self.clear_button)

        self.setCentralWidget(self.main_widget)

        self.draw_button.clicked.connect(self.update_filled_pixels)
        self.clear_button.clicked.connect(self.clear_canvas)

        self.line_color_counter = 0

        self.lines : list[Line]= []
        self.filled_pixels = []

        self.canvas.mpl_connect("button_press_event", self.get_coordinates)
        self.canvas.mpl_connect("button_release_event", self.finish_line)

        self.show()

    def get_coordinates(self, event):
        x = event.xdata
        y = event.ydata

        self.start_x = x
        self.start_y = y
        

    def finish_line(self, event):
        x = event.xdata
        y = event.ydata

        end_x = x
        end_y = y

        color = plt.cm.tab10(self.line_color_counter)
        self.line_color_counter += 1
        print("Starting point coordinates: ({}, {})".format(self.start_x, self.start_y))
        print("Ending point coordinates: ({}, {})".format(end_x, end_y))
        self.canvas.axes.plot([self.start_x, end_x], [self.start_y, end_y], color=color)
        self.lines.append(Line(self.start_x, self.start_y, end_x, end_y, color))
        self.canvas.draw()

    def clear_canvas(self):
        self.canvas.axes.clear()
        self.canvas.reset()
        self.canvas.draw()

        self.lines = []
        self.filled_pixels = []

        self.line_color_counter = 0

    def update_filled_pixels(self):
        start = time()
        algo = self.rasterize_dropdown.currentIndex()

        for l in self.lines:
            self.filled_pixels.extend(rasterize_line(l.start_x, l.start_y, l.end_x, l.end_y, l.color, algo))
        self.lines.clear()

        for pixel in self.filled_pixels:
            x, y, color = pixel
            self.canvas.axes.fill([x, x + 1, x + 1, x], [y, y, y + 1, y + 1], color=color, edgecolor='lightgray')
        self.filled_pixels.clear()

        self.canvas.draw()
        end = time()
        print(F"Time elapsed {end-start}")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec()
