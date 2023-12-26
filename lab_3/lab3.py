import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QButtonGroup, QMainWindow, QFileDialog, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton, QSplitter, QSpinBox
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QSize
from enum import Enum
from combined_file_dialog import CombinedFileDialog

class ProcessingType(Enum):
    MORPHOLOGY_CLOSE = 1
    MORPHOLOGY_OPEN = 2
    EDGE_DETECT = 3
    LINEAR_CONTRAST_RGB = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create radio button group
        self.radio_widget = QWidget()
        self.radio_widget_layout = QVBoxLayout()
        self.radio_widget.setLayout(self.radio_widget_layout)

        self.radio_btn1 = QRadioButton("Morphology Opening with different sizes")
        self.radio_widget_layout.addWidget(self.radio_btn1)
        self.radio_btn2 = QRadioButton("Morphology Closing with different sizes")
        self.radio_widget_layout.addWidget(self.radio_btn2)
        self.radio_btn3 = QRadioButton("Sobel and Canny Filters")
        self.radio_widget_layout.addWidget(self.radio_btn3)
        self.radio_btn4 = QRadioButton("Adding a constant + Linear Contrast RGB")
        self.radio_widget_layout.addWidget(self.radio_btn4)
        #self.radio_btn5 = QRadioButton("Linear Contrast HSV")
        #self.radio_widget_layout.addWidget(self.radio_btn5)

        self.radio_group = QButtonGroup(self.radio_widget)
        self.radio_group.addButton(self.radio_btn1, 1)
        self.radio_group.addButton(self.radio_btn2, 2)
        self.radio_group.addButton(self.radio_btn3, 3)
        self.radio_group.addButton(self.radio_btn4, 4)
        self.radio_group.button(1).setChecked(True)

        # Create labels
        self.label1 = QLabel()
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setMaximumSize(QSize(550, 960))
        self.label2 = QLabel()
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setMaximumSize(QSize(550, 960))
        self.label3 = QLabel()
        self.label3.setAlignment(Qt.AlignCenter)
        self.label3.setMaximumSize(QSize(550, 960))

        # Create layout for labels
        self.label_layout = QHBoxLayout()
        self.label_layout.addWidget(self.label1)
        self.label_layout.addWidget(self.label2)
        self.label_layout.addWidget(self.label3)

        # Create button for file dialog
        self.choose_image_btn = QPushButton("Choose Image")
        self.choose_image_btn.clicked.connect(self.open_file_dialog)

        # Create SpinBox for structuring element size
        self.struct_element_width_spinbox = QSpinBox()
        self.struct_element_width_spinbox.setMinimum(2)
        self.struct_element_width_spinbox.setMaximum(9999)
        self.struct_element_width_spinbox.setValue(10)
        self.struct_element_height_spinbox = QSpinBox()
        self.struct_element_height_spinbox.setMinimum(4)
        self.struct_element_height_spinbox.setMaximum(9999)
        self.struct_element_height_spinbox.setValue(10)

        # Create layout for spinbox
        self.spinbox_layout = QHBoxLayout()
        self.spinbox_layout.setSpacing(200)
        self.spinLabel = QLabel("Structuring Element Size:")
        self.spinbox_layout.addWidget(self.spinLabel)
        self.spinbox_layout.addWidget(self.struct_element_width_spinbox)
        self.spinbox_layout.addWidget(self.struct_element_height_spinbox)

        # Create main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.radio_widget)
        self.main_layout.addLayout(self.spinbox_layout)
        self.main_layout.addWidget(self.choose_image_btn)
        self.main_layout.addLayout(self.label_layout)

        # Create splitter for labels
        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.setHandleWidth(0)
        self.splitter1.addWidget(self.label1)
        self.splitter1.addWidget(self.label2)
        self.splitter1.addWidget(self.label3)
        self.splitter1.setSizes([300, 300, 300])

        # Create splitter for spinbox
        self.splitter3 = QSplitter(Qt.Horizontal)
        self.splitter3.setHandleWidth(10)
        #self.splitter3.setContentsMargins(20,20,20,20)
        self.splitter3.addWidget(self.spinLabel)
        self.splitter3.addWidget(self.struct_element_width_spinbox)
        self.splitter3.addWidget(self.struct_element_height_spinbox)
        #self.splitter1.setSizes([150,150, 100])

        # Create splitter for main layout
        self.splitter2 = QSplitter(Qt.Vertical)
        self.splitter2.setHandleWidth(0)
        self.splitter2.addWidget(self.radio_widget)
        self.splitter2.addWidget(self.splitter3)
        self.splitter2.addWidget(self.choose_image_btn)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.setSizes([50, 50, 50, 500])

        # Set main layout as central widget
        self.setCentralWidget(self.splitter2)

        self.radio_group.idClicked.connect(self.radio_group_change)
        self.struct_element_width_spinbox.valueChanged.connect(self.spinbox_value_changed)
        self.struct_element_height_spinbox.valueChanged.connect(self.spinbox_value_changed)

        # Set window properties
        self.setWindowTitle("Image Processing")
        self.setGeometry(100, 100, 800, 600)
        self.image = None

    def open_file_dialog(self):
        # Open file dialog to choose image
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg *.gif)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]

            # Load image using OpenCV
            self.image = cv2.imread(file_path)

            self.struct_element_height_spinbox.setMaximum(int(np.max(self.image.shape)))
            self.struct_element_width_spinbox.setMaximum(int(np.max(self.image.shape)))

            # Display original image in label1
            self.display_image(self.image, self.label1)
            img2, img3 = self.process_image(self.image, ProcessingType(self.radio_group.checkedId()))
            self.display_image(img2, self.label2)
            self.display_image(img3, self.label3)

    def spinbox_value_changed(self):
        if self.image is not None:
            img2, img3 = self.process_image(self.image, ProcessingType(self.radio_group.checkedId()))
            self.display_image(img2, self.label2)
            self.display_image(img3, self.label3)

    def radio_group_change(self, button_id : int):
        if self.image is not None:
            img2, img3 = self.process_image(self.image, ProcessingType(button_id))
            self.display_image(img2, self.label2)
            self.display_image(img3, self.label3)

    def process_image(self, image, type : ProcessingType):
        if type == ProcessingType.MORPHOLOGY_OPEN:
            return self.morphology(image, (cv2.MORPH_OPEN, cv2.MORPH_OPEN), (0.005, 0.01), (cv2.MORPH_RECT, cv2.MORPH_RECT))
        
        if type == ProcessingType.MORPHOLOGY_CLOSE:
            return self.morphology(image, (cv2.MORPH_CLOSE, cv2.MORPH_CLOSE), (0.005, 0.01), (cv2.MORPH_RECT, cv2.MORPH_RECT))
            
        if type == ProcessingType.LINEAR_CONTRAST_RGB:
            return self.add_constant(image)
        
        elif type == ProcessingType.EDGE_DETECT:
            return self.edge_detect(image)

    def add_constant(self,image):
        nparr = np.ones(image.shape,dtype=np.uint8) * 100
        opencvImg = cv2.add(image,nparr)
        bgr = cv2.split(opencvImg)
        contrasted_array = self.linear_contrast(bgr, (1,1,1))
        return opencvImg, cv2.merge(contrasted_array)
    
    def morphology(self, image, operation, size_coefs, struct_elements):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        kernel = []
        k = int(np.max(image.shape))
        # size = (int(size_coefs[0] * k), int(size_coefs[1] * k))
        size = (self.struct_element_width_spinbox.value(),self.struct_element_height_spinbox.value())
        if size[0] < 2 or size[1] < 4:
            size = (2,4)
        print(f"Filter size: {size}")
        kernel.append(cv2.getStructuringElement( struct_elements[0], size))
        kernel.append(cv2.getStructuringElement( struct_elements[1], tuple(reversed(size))))
        print(f"Kernel {kernel[0]}")

        opened = cv2.morphologyEx(gray, operation[0], kernel[0])
        closed = cv2.morphologyEx(gray, operation[1], kernel[1])

        return opened, closed

    def edge_detect(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

        sobel_x = cv2.Scharr(gray_image, cv2.CV_8U, 1, 0, 1.0)
        sobel_y = cv2.Scharr(gray_image, cv2.CV_8U, 0, 1, 1.0)
        sobel_image = cv2.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)

        canny_image = cv2.Canny(gray_image, 50, 150)
        return sobel_image, canny_image

    def linear_contrast(self,channels, mask=(1,1,1)):
        MAX = 255
        MIN = 0

        result = []
        for ch, is_change in zip(channels, mask):
            if not is_change:
                result.append(ch)
                continue

            min = float(ch.min())
            max = float(ch.max())
            if (max - min) == 0:
                result.append(ch)
                continue

            ch = cv2.convertScaleAbs(ch, alpha=1.0, beta=-min)

            alpha = (MAX - MIN) / (max - min)
            beta = MIN
            result.append(cv2.convertScaleAbs(ch, alpha=alpha, beta=beta))
        return result

    def display_image(self, image, label : QLabel, color_space = None):
        q_image = self.convert_cv_to_qimage(image, color_space)
        pixmap = QPixmap.fromImage(q_image)
        if pixmap.width() > label.maximumWidth() or pixmap.height() > label.maximumHeight():
            pixmap = pixmap.scaled(label.maximumSize(), Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap)

    def convert_cv_to_qimage(self, cv_image, color_space=None):
        if color_space is None:
            color_space = cv2.COLOR_BGR2RGB

        if len(cv_image.shape) == 2:
            height, width = cv_image.shape
            bytes_per_line = width
            q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            cv_image = cv2.cvtColor(cv_image, color_space)
            height, width, channel = cv_image.shape
            bytes_per_line = channel * width
            q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        #q_image = q_image.convertToFormat(QImage.Format_ARGB32)
        return q_image

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

