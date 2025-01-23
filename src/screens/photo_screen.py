from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
    QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
import logging
from config import Config
import os
import threading
import time

class PhotoScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # 카메라 초기화를 생성자에서 미리 수행
        self.initialize_camera()
        self.initUI()
    
    def initialize_camera(self):
        """카메라 초기화"""
        logging.info("카메라 초기화 시작...")
        try:
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            if not self.camera.isOpened():
                self.camera = cv2.VideoCapture(0)
            
            if self.camera.isOpened():
                # 카메라 설정 최적화
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 버퍼 크기 최소화
                self.camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
                
                # 초기 프레임 읽기로 카메라 워밍업
                for _ in range(5):  # 처음 몇 프레임을 버림
                    self.camera.read()
                    
                logging.info("카메라 초기화 완료")
            else:
                logging.error("카메라를 찾을 수 없습니다")
                
        except Exception as e:
            logging.error(f"카메라 초기화 오류: {str(e)}")
        
    def initUI(self):
        # 배경 이미지 설정
        bg_image_path = os.path.join(Config.RESOURCES_DIR, 'main.png')
        self.background = QLabel(self)
        self.background.setFixedSize(Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT)
        pixmap = QPixmap(bg_image_path).scaled(
            Config.DISPLAY_WIDTH,
            Config.DISPLAY_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.background.setPixmap(pixmap)
        self.background.move(0, 0)
        
        # 카메라 프리뷰 프레임
        self.preview_frame = QLabel(self)
        self.preview_frame.setFixedSize(Config.PREVIEW_WIDTH, Config.PREVIEW_HEIGHT)
        self.preview_frame.setStyleSheet("""
            QLabel {
                background-color: black;
                border: 1px solid gray;
            }
        """)
        self.preview_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_frame.move(
            (Config.DISPLAY_WIDTH - Config.PREVIEW_WIDTH) // 2,
            (Config.DISPLAY_HEIGHT - Config.PREVIEW_HEIGHT) // 2 - 80
        )
        
        # 촬영 버튼
        self.capture_button = QPushButton("촬영하기", self)
        self.capture_button.setFixedSize(600, 120)
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #5B9279;
                color: white;
                border: 4px solid #4A7A64;
                border-radius: 60px;
                font-size: 48px;
                font-weight: bold;
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background-color: #4A7A64;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #3A6A54;
                transform: scale(0.98);
            }
        """)
        self.capture_button.move(
            (Config.DISPLAY_WIDTH - 600) // 2,
            Config.DISPLAY_HEIGHT - 250
        )

        self.capture_button.clicked.connect(self.capture_photo)

            # 메시지 표시 라벨 추가
        self.message_label = QLabel(self)
        self.message_label.setFixedSize(Config.DISPLAY_WIDTH, 50)  # 메시지 영역 높이 50
        self.message_label.move(0, 10)  # 화면 위쪽에 위치
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 0.7);
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.message_label.hide()  # 초기에는 메시지를 숨김
        
    def showEvent(self, event):
        """위젯이 표시될 때 카메라 시작"""
        super().showEvent(event)
        if not self.timer.isActive():
            if not self.camera or not self.camera.isOpened():
                self.initialize_camera()
            self.timer.start(int(1000/Config.CAMERA_FPS))
    
    def update_frame(self):
        """카메라 프레임 업데이트 최적화"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # 프레임 처리 최적화
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                
                # QImage 생성 (직접 메모리 참조)
                qt_image = QImage(rgb_image.data, w, h, w * ch, QImage.Format.Format_RGB888)
                
                # 스케일링 최적화
                scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                    Config.PREVIEW_WIDTH,
                    Config.PREVIEW_HEIGHT,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation  # 빠른 변환 사용
                )
                
                self.preview_frame.setPixmap(scaled_pixmap)
    
    def capture_photo(self):
        """사진 촬영 (텍스트 메시지 고정)"""
        def update_message(remaining_time):
            """남은 시간 메시지 업데이트"""
            self.message_label.setText(f"{remaining_time}초 후에 찍힙니다")
            self.message_label.show()

        def hide_message():
            """메시지 숨기기"""
            self.message_label.hide()

        def take_photo():
            """사진 촬영"""
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    # 메시지 숨기기
                    hide_message()

                    # 원본 이미지를 그대로 저장
                    self.parent.current_image = frame

                    # 정보 입력 화면으로 전환
                    self.parent.show_frame("InfoFrame")
        
        def countdown():
            """3초 카운트다운"""
            remaining_time = 3
            timer = QTimer(self)
            
            def on_timeout():
                nonlocal remaining_time
                update_message(remaining_time)  # 메시지 업데이트
                remaining_time -= 1
                if remaining_time < 0:
                    timer.stop()  # 타이머 정지
                    take_photo()  # 사진 촬영
            
            timer.timeout.connect(on_timeout)
            timer.start(1000)  # 1초마다 실행
        
        countdown()  # 카운트다운 시작



    def hideEvent(self, event):
        """위젯이 숨겨질 때 타이머만 중지"""
        super().hideEvent(event)
        if self.timer.isActive():
            self.timer.stop()
    
    def show_error(self, message):
        """에러 메시지 표시"""
        self.preview_frame.setText(message)
        self.preview_frame.setStyleSheet("""
            QLabel {
                color: white;
                background-color: black;
                font-size: 20px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
                padding: 20px;
            }
        """)
            
    def closeEvent(self, event):
        """프로그램 종료 시에만 카메라 해제"""
        if self.camera and self.camera.isOpened():
            self.timer.stop()
            self.camera.release()
            self.camera = None
        event.accept()