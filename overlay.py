from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor
import sys

class BlurOverlay(QWidget):
    def __init__(self):
        super().__init__()
        
        # Frameless, stays on top, tool window (doesn't show in taskbar), transparent background
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Fullscreen on all monitors (simplified to primary screen here, but can expand)
        self.showFullScreen()
        
        self.current_opacity = 0.0
        self.target_opacity = 0.0
        
    def paintEvent(self, event):
        if self.current_opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Semi-transparent black background
            # 0.0 is completely transparent, 1.0 is completely black
            # Max opacity we should allow is maybe 0.7 so it's not totally black
            alpha = int(self.current_opacity * 255)
            painter.fillRect(self.rect(), QColor(0, 0, 0, alpha))
            
    def set_blur_level(self, level):
        """Set blur level from 0.0 (none) to 1.0 (max)"""
        # Constrain level
        level = max(0.0, min(level, 0.8))  # Max 80% opacity
        
        if abs(level - self.target_opacity) > 0.05:
            self.target_opacity = level
            self.current_opacity = level
            self.update()
