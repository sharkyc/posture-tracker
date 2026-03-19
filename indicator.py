from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QMovie
import os
import random

class GifWindow(QWidget):
    def __init__(self, parent_indicator):
        super().__init__()
        self.parent_indicator = parent_indicator
        
        # 窗口置顶、无边框、工具窗口、鼠标穿透
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 显示 GIF 的 Label
        self.label = QLabel(self)
        self.label.setAttribute(Qt.WA_TranslucentBackground)
        # 让内容自适应 Label 大小
        self.label.setScaledContents(True)
        self.movie = None
        
        self.gifs_dir = os.path.join(os.path.dirname(__file__), 'gifs')
        
    def show_random_gif(self):
        if not os.path.exists(self.gifs_dir):
            return
            
        gifs = [f for f in os.listdir(self.gifs_dir) if f.lower().endswith('.gif')]
        if not gifs:
            return
            
        selected_gif = random.choice(gifs)
        gif_path = os.path.join(self.gifs_dir, selected_gif)
        
        # 停止旧动画
        if self.movie:
            self.movie.stop()
            
        self.movie = QMovie(gif_path)
        
        # 验证动画是否有效
        if not self.movie.isValid():
            print(f"Failed to load GIF: {gif_path}")
            return
            
        self.label.setMovie(self.movie)
        self.movie.start()
        
        # 强制设置一个默认尺寸并显示，避免等待加载失败导致不可见
        self.resize(200, 200)
        self.label.resize(200, 200)
        self.show()
        
        # 调整大小和位置
        QTimer.singleShot(100, self._adjust_size_and_position)
        
    def _adjust_size_and_position(self):
        if not self.movie:
            return
            
        # 尝试获取图片真实尺寸
        size = self.movie.currentImage().size()
        
        width = 200
        height = 200
        if not size.isEmpty():
            # 限制最大宽高，避免过大
            width = min(size.width(), 300)
            height = min(size.height(), 300)
            
        self.resize(width, height)
        self.label.resize(width, height)
        
        # 定位到指示灯的左侧
        indicator_geo = self.parent_indicator.geometry()
        x = indicator_geo.left() - width - 10
        y = indicator_geo.bottom() - height
        self.move(x, y)
        
    def hide_gif(self):
        if self.movie:
            self.movie.stop()
        self.hide()


class IndicatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 窗口置顶、无边框、工具窗口、鼠标穿透
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置指示灯大小：竖向条状
        self.width = 10
        self.height = 150
        self.resize(self.width, self.height)
        
        # 定位到屏幕右下角
        self.position_bottom_right()
        
        # 状态
        self.current_color = QColor(0, 255, 0, 180)  # 默认绿色，半透明
        self.is_blinking = False
        self.blink_state = True
        
        # 闪烁定时器
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_blink)
        
        # GIF 窗口
        self.gif_window = GifWindow(self)
        self.is_showing_gif = False
        
    def position_bottom_right(self):
        screen = QApplication.primaryScreen().geometry()
        # 距离右边 20px，距离底部 60px (避开任务栏)
        x = screen.width() - self.width - 20
        y = screen.height() - self.height - 60
        self.move(x, y)
        
    def update_status(self, ratio, is_severe):
        """
        ratio: 0.0 (好) 到 1.0 (最差)
        is_severe: 是否严重驼背
        """
        # 计算颜色：绿 -> 黄 -> 红
        # ratio = 0   -> RGB(0, 255, 0)
        # ratio = 0.5 -> RGB(255, 255, 0)
        # ratio = 1.0 -> RGB(255, 0, 0)
        
        if ratio < 0.5:
            # 绿到黄 (红增加)
            r = int((ratio * 2) * 255)
            g = 255
        else:
            # 黄到红 (绿减少)
            r = 255
            g = int((1.0 - (ratio - 0.5) * 2) * 255)
            
        b = 0
        
        # 确保在合法范围内
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        
        self.current_color = QColor(r, g, b, 200)
        
        # 处理闪烁和 GIF 显示
        if is_severe:
            if not self.is_blinking:
                self.is_blinking = True
                self.blink_timer.start(300) # 300ms 闪烁一次
            
            if not self.is_showing_gif:
                self.is_showing_gif = True
                self.gif_window.show_random_gif()
        else:
            if self.is_blinking:
                self.is_blinking = False
                self.blink_timer.stop()
                self.blink_state = True # 恢复常亮
                
            if self.is_showing_gif:
                self.is_showing_gif = False
                self.gif_window.hide_gif()
                
        self.update()
        
    def toggle_blink(self):
        self.blink_state = not self.blink_state
        self.update()

    def paintEvent(self, event):
        if not self.blink_state:
            return # 闪烁时隐藏
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角矩形指示灯
        rect = QRect(0, 0, self.width, self.height)
        painter.setBrush(self.current_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 5, 5)
        
    def hide_indicator(self):
        self.blink_timer.stop()
        self.gif_window.hide_gif()
        self.is_showing_gif = False
        self.hide()
        
    def show_indicator(self):
        self.show()
