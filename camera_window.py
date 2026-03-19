from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2

class CameraWindow(QWidget):
    # Signal emitted when window is closed by double click
    closed_signal = pyqtSignal()
    
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
        
        # 悬停提示相关
        self.has_shown_hint = False
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_close_hint)
        
        # 提示标签 (初始隐藏)
        self.hint_label = QLabel("双击可关闭画面", self)
        self.hint_label.setStyleSheet("color: rgba(255, 255, 255, 180); font-size: 12px; background: transparent;")
        self.hint_label.adjustSize()
        self.hint_label.hide()
        
    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

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
        
    def resizeEvent(self, event):
        # 保持提示在底部中间
        self.hint_label.move(
            (self.width() - self.hint_label.width()) // 2,
            self.height() - self.hint_label.height() - 10
        )
        super().resizeEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()
            self.closed_signal.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def enterEvent(self, event):
        # 鼠标进入，开始计时
        if not self.has_shown_hint:
            self.hover_timer.start(3000) # 3秒
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        # 鼠标离开，停止计时
        self.hover_timer.stop()
        super().leaveEvent(event)

    def show_close_hint(self):
        if not self.has_shown_hint:
            self.hint_label.show()
            self.has_shown_hint = True
            # 显示3秒后自动隐藏
            QTimer.singleShot(3000, self.hint_label.hide)

    def show(self):
        # 每次重新显示窗口时重置状态
        self.has_shown_hint = False
        super().show()
