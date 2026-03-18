from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2

class CameraWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 窗口置顶、无边框、工具窗口（不显示在任务栏）
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        
        # 初始大小
        self.resize(320, 240)
        
        # 初始位置（右上角附近）
        # 这里只是一个简单的默认位置，实际上可以根据屏幕分辨率来调整
        self.move(100, 100)
        
        # 布局和显示图片的Label
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.image_label)
        
        # 用于实现拖动窗口的变量
        self.drag_position = None
        
    def update_frame(self, rgb_image):
        """接收RGB图像并更新显示"""
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        # 转换为 QImage
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # 缩放到窗口大小并保持比例
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()
