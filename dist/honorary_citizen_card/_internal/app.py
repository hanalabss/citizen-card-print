from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QPushButton
from PyQt6.QtCore import Qt
from screens.photo_screen import PhotoScreen
from screens.info_screen import InfoScreen
from screens.main_screen import MainScreen
from config import Config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # 전역 변수 초기화
        self.current_image = None
        self.camera = None
        
    def initUI(self):
        # 윈도우 설정
        self.setFixedSize(Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT)
        
        # 중앙 위젯으로 스택 위젯 설정
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # 화면들 생성 및 추가
        self.frames = {}
        
        main_screen = MainScreen(self)
        photo_screen = PhotoScreen(self)
        info_screen = InfoScreen(self)
        
        self.central_widget.addWidget(main_screen)
        self.central_widget.addWidget(photo_screen)
        self.central_widget.addWidget(info_screen)
        
        self.frames = {
            "MainScreen": 0,
            "PhotoFrame": 1,
            "InfoFrame": 2
        }
        
        # 초기 화면 설정
        self.show_frame("MainScreen")
        
        # 닫기 버튼 추가
        self.add_close_button()
        
    def add_close_button(self):
        """오른쪽 상단에 닫기 버튼 추가"""
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(40, 40)
        self.close_button.move(self.width() - 50, 10)  # 오른쪽 상단 위치
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5c5c;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e04a4a;
            }
        """)
        self.close_button.clicked.connect(self.close_application)
    
    def close_application(self):
        """앱 종료 동작"""
        self.close()
        
    def show_frame(self, frame_name):
        """화면 전환 함수"""
        if frame_name in self.frames:
            self.central_widget.setCurrentIndex(self.frames[frame_name])
    
    def keyPressEvent(self, event):
        """ESC 키 이벤트 처리"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
    
    def closeEvent(self, event):
        """프로그램 종료 시 카메라 해제"""
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.release()
        event.accept()
