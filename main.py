import sys
import os
import math

# 解决 PyQt5 找不到 windows 插件和 imageformats 的问题
import PyQt5
dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins')
os.environ['QT_PLUGIN_PATH'] = plugin_path
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(plugin_path, 'platforms')

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QStyle, QMessageBox, QActionGroup
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor
from posture_tracker import PostureTracker
from overlay import BlurOverlay
from camera_window import CameraWindow
from indicator import IndicatorWindow

class PostureApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Initialize Overlay
        self.overlay = BlurOverlay()
        
        # Initialize Camera Window
        self.camera_window = CameraWindow()
        # 默认不显示摄像头画面，如果需要默认显示可以改为 True
        self.is_camera_visible = False
        
        # Initialize Indicator Window
        self.indicator = IndicatorWindow()
        
        # Initialize Tracker
        self.tracker = PostureTracker()
        self.tracker.posture_status_signal.connect(self.handle_posture_update)
        self.tracker.error_signal.connect(self.handle_error)
        self.tracker.frame_signal.connect(self.handle_frame_update)
        
        # App state
        self.latest_score = 0.0
        self.is_monitoring = True
        self.reminder_mode = "blur" # "blur" or "indicator"
        
        # Setup System Tray
        self.setup_tray()
        
        # Start Tracker
        self.tracker.start()
        
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        
        # Create a solid color icon if standard icon fails to show on Windows
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("blue"))
        icon = QIcon(pixmap)
        
        # Try to use standard icon, fallback to custom pixmap if it's somehow empty
        standard_icon = self.app.style().standardIcon(QStyle.SP_ComputerIcon)
        if not standard_icon.isNull():
            icon = standard_icon
            
        self.tray_icon.setIcon(icon)
        
        # Windows requires the tray icon to have a tooltip or it might be hidden in some cases
        self.tray_icon.setToolTip("坐直提醒")
        
        self.tray_menu = QMenu()
        
        # Status action (disabled)
        self.status_action = QAction("状态: 正在监控")
        self.status_action.setEnabled(False)
        self.tray_menu.addAction(self.status_action)
        
        self.tray_menu.addSeparator()
        
        # Calibrate action
        self.calibrate_action = QAction("重新校准 (坐直并点击)")
        self.calibrate_action.triggered.connect(self.calibrate)
        self.tray_menu.addAction(self.calibrate_action)
        
        # Toggle monitoring
        self.toggle_action = QAction("暂停监控")
        self.toggle_action.triggered.connect(self.toggle_monitoring)
        self.tray_menu.addAction(self.toggle_action)
        
        self.tray_menu.addSeparator()
        
        # Reminder Mode Submenu
        self.mode_menu = QMenu("提醒模式", self.tray_menu)
        self.mode_group = QActionGroup(self.app)
        
        self.mode_blur_action = QAction("全屏变暗", self.mode_menu, checkable=True)
        self.mode_blur_action.setChecked(True)
        self.mode_blur_action.setData("blur")
        self.mode_group.addAction(self.mode_blur_action)
        self.mode_menu.addAction(self.mode_blur_action)
        
        self.mode_indicator_action = QAction("右下角指示灯", self.mode_menu, checkable=True)
        self.mode_indicator_action.setData("indicator")
        self.mode_group.addAction(self.mode_indicator_action)
        self.mode_menu.addAction(self.mode_indicator_action)
        
        self.mode_group.triggered.connect(self.change_mode)
        self.tray_menu.addMenu(self.mode_menu)
        
        self.tray_menu.addSeparator()
        
        # Toggle camera view
        self.camera_action = QAction("显示摄像头画面")
        self.camera_action.triggered.connect(self.toggle_camera)
        self.tray_menu.addAction(self.camera_action)
        
        self.tray_menu.addSeparator()
        
        # Quit action
        self.quit_action = QAction("退出")
        self.quit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        # Show a notification
        self.tray_icon.showMessage(
            "坐直提醒已启动",
            "请坐直并右键托盘图标点击「重新校准」。",
            QSystemTrayIcon.Information,
            3000
        )

    def calibrate(self):
        if self.latest_score > 0:
            self.tracker.calibrate(self.latest_score)
            self.tray_icon.showMessage(
                "校准完成",
                "已记录当前坐姿，请保持。",
                QSystemTrayIcon.Information,
                2000
            )
            # Instantly clear blur or set indicator to green
            if self.reminder_mode == "blur":
                self.overlay.set_blur_level(0.0)
            elif self.reminder_mode == "indicator":
                self.indicator.update_status(0.0, False)
        else:
            self.tray_icon.showMessage(
                "校准失败",
                "未检测到人体姿态，请确保摄像头能看到您的肩膀和面部。",
                QSystemTrayIcon.Warning,
                3000
            )

    def change_mode(self, action):
        self.reminder_mode = action.data()
        if self.reminder_mode == "blur":
            self.indicator.hide_indicator()
            # If paused, ensure blur is off
            if not self.is_monitoring:
                self.overlay.set_blur_level(0.0)
        elif self.reminder_mode == "indicator":
            self.overlay.set_blur_level(0.0)
            if self.is_monitoring:
                self.indicator.show_indicator()
            else:
                self.indicator.hide_indicator()

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.toggle_action.setText("暂停监控")
            self.status_action.setText("状态: 正在监控")
            if self.reminder_mode == "indicator":
                self.indicator.show_indicator()
        else:
            self.toggle_action.setText("恢复监控")
            self.status_action.setText("状态: 已暂停")
            # Clear blur and hide indicator when paused
            self.overlay.set_blur_level(0.0)
            self.indicator.hide_indicator()

    def toggle_camera(self):
        self.is_camera_visible = not self.is_camera_visible
        if self.is_camera_visible:
            self.camera_action.setText("隐藏摄像头画面")
            self.camera_window.show()
        else:
            self.camera_action.setText("显示摄像头画面")
            self.camera_window.hide()

    def handle_frame_update(self, rgb_image):
        if self.is_camera_visible:
            self.camera_window.update_frame(rgb_image)

    def handle_posture_update(self, current_score, baseline):
        self.latest_score = current_score
        
        if not self.is_monitoring:
            return
            
        if baseline == 0.0:
            # Not calibrated yet
            self.status_action.setText("状态: 等待校准")
            return
            
        # Determine slouching level
        # Assuming baseline is higher (good posture), and current_score is lower (slouching)
        # Dead zone: 10% drop
        # Max slouch: 30% drop
        dead_zone_score = baseline * 0.90
        max_slouch_score = baseline * 0.70
        
        # Calculate ratio: 0.0 (good) to 1.0 (max slouch)
        if current_score >= dead_zone_score:
            ratio = 0.0
        elif current_score <= max_slouch_score:
            ratio = 1.0
        else:
            ratio = (dead_zone_score - current_score) / (dead_zone_score - max_slouch_score)
            
        is_severe = current_score <= max_slouch_score
        
        if current_score >= dead_zone_score:
            self.status_action.setText("状态: 姿势良好")
        elif is_severe:
            self.status_action.setText("状态: 严重驼背！")
        else:
            self.status_action.setText("状态: 请坐直！")
            
        # Apply visual feedback based on selected mode
        if self.reminder_mode == "blur":
            blur_level = ratio * 0.8
            self.overlay.set_blur_level(blur_level)
        elif self.reminder_mode == "indicator":
            self.indicator.update_status(ratio, is_severe)

    def handle_error(self, err_msg):
        self.tray_icon.showMessage("错误", err_msg, QSystemTrayIcon.Critical, 5000)

    def quit_app(self):
        self.tracker.stop()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    app = PostureApp()
    app.run()
