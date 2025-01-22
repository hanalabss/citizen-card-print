from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
from config import Config

class MainScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 배경 이미지 설정
        image_path = os.path.join(Config.RESOURCES_DIR, 'main.png')
        background = QLabel(self)
        pixmap = QPixmap(image_path)
        background.setPixmap(pixmap.scaled(
            Config.DISPLAY_WIDTH, 
            Config.DISPLAY_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        
        layout.addWidget(background, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 클릭 이벤트를 위한 설정
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        """화면 클릭 시 다음 화면으로 이동"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent.show_frame("PhotoFrame")