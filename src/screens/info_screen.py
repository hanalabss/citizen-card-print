import os

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFrame, QSlider, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
from PIL import Image
import numpy as np
from screens.virtual_keyboard import VirtualKeyboard
from utils.excel import ExcelManager
from utils.card_printer import print_honorary_citizen_card
from config import Config

class InfoScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.rotation_angle = 0
        self.drag_start_pos = None
        self.image_position = {"x": 0, "y": 0}
        self.scale_factor = 3  # 실제 크기의 3배로 화면에 표시
        self.zoom_level = 1.0  # 기본 줌 레벨
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 배경 생성
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap(os.path.join(Config.RESOURCES_DIR, 'bg.png')).scaled(
            Config.DISPLAY_WIDTH,
            Config.DISPLAY_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding
        ))
        self.background.move(0, 0)
        
        # 메인 컨테이너 생성 (preview와 폼을 감싸는 컨테이너)
        main_container = QFrame(self)
        main_container.setStyleSheet("background: transparent;")
        main_container.setFixedSize(900, 600)  # 전체 컨테이너 크기
        main_container.move(
            (Config.DISPLAY_WIDTH - 900) // 2,
            50
        )
        
        # 수평 레이아웃 생성
        h_layout = QHBoxLayout(main_container)
        h_layout.setSpacing(40)  # preview와 폼 사이 간격
        
        # === 왼쪽: Preview 영역 ===
        left_container = QFrame()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)  # 위젯 간 간격
        
        # Preview Area
        photo_ratio = Config.PHOTO_HEIGHT / Config.PHOTO_WIDTH
        preview_width = 400
        preview_height = int(preview_width * photo_ratio)
        
        preview_container = QFrame()
        preview_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #888;
                border-radius: 5px;
            }
        """)
        preview_container.setFixedSize(preview_width, preview_height)
        
        self.preview_frame = QFrame(preview_container)
        self.preview_frame.setFixedSize(preview_width, preview_height)
        
        self.preview_label = QLabel(self.preview_frame)
        self.preview_label.setFixedSize(preview_width, preview_height)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mouse events
        self.preview_label.mousePressEvent = self.start_drag
        self.preview_label.mouseMoveEvent = self.drag
        self.preview_label.mouseReleaseEvent = self.stop_drag
        
        # Controls - preview frame 아래에 배치
        controls_container = QFrame()
        controls_container.setFixedWidth(preview_width)  # preview와 같은 너비
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # 줌 슬라이더 컨테이너
        zoom_container = QFrame()
        zoom_layout = QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(10)
        
        zoom_label = QLabel("확대/축소")
        zoom_label.setStyleSheet("color: #333; font-size: 13px;")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 100)
        self.zoom_slider.setValue(10)
        self.zoom_slider.setFixedWidth(200)  # 슬라이더 너비 고정
        self.zoom_slider.valueChanged.connect(self.update_preview)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #ddd;
            }
            QSlider::handle:horizontal {
                background: #5B9279;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
        """)
        
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)
        
        rotate_btn = QPushButton("회전")
        rotate_btn.clicked.connect(self.rotate_image)
        rotate_btn.setFixedWidth(80)  # 버튼 너비 고정
        rotate_btn.setStyleSheet("""
            QPushButton {
                background-color: #5B9279;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4A7A64;
            }
        """)
        
        controls_layout.addWidget(zoom_container)
        controls_layout.addWidget(rotate_btn)
        
        # 왼쪽 컨테이너에 위젯 추가
        left_layout.addWidget(preview_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addWidget(controls_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch()  # 남은 공간 채우기
        
        # === 오른쪽: 입력 폼 영역 ===
        right_container = QFrame()
        form_layout = QVBoxLayout(right_container)
        form_layout.setSpacing(10)

        # 공통 스타일시트 선언
        input_style = """
        QLineEdit {
        font-size: 62px;
        font-family: '맑은 고딕';
        padding: 5px;
        border: 2px solid #ccc;
        border-radius: 8px;
        }
        """

        # 이름 입력
        name_label = QLabel("이름")
        name_label.setStyleSheet("font-weight: bold; font-size: 40px;")
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(80)
        self.name_input.setStyleSheet(input_style)

        # 생년월일 입력 
        birth_label = QLabel("생년월일")
        birth_label.setStyleSheet("font-weight: bold; font-size: 40px;")
        birth_hint = QLabel("예시) 19901231")
        birth_hint.setStyleSheet("color: gray; font-size: 20px;")
        self.birth_input = QLineEdit()
        self.birth_input.setFixedHeight(80)
        self.birth_input.setStyleSheet(input_style)
        
        # 버튼 컨테이너
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(20)
        
        # 버튼들
        issue_btn = QPushButton("발급")
        retake_btn = QPushButton("재촬영")
        reset_btn = QPushButton("초기화")
        
        for btn in [issue_btn, retake_btn, reset_btn]:
            btn.setFixedSize(135, 90)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #5B9279;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 28px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4A7A64;
                }
            """)
        
        issue_btn.clicked.connect(self.process_and_print)
        retake_btn.clicked.connect(lambda: self.parent.show_frame("PhotoFrame"))
        reset_btn.clicked.connect(self.reset_form)
        
        button_layout.addWidget(issue_btn)
        button_layout.addWidget(retake_btn)
        button_layout.addWidget(reset_btn)
        
        # 폼에 위젯 추가
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(birth_label)
        form_layout.addWidget(birth_hint)
        form_layout.addWidget(self.birth_input)
        form_layout.addWidget(button_container)
        form_layout.addStretch()  # 버튼과 입력 필드 사이 공간
        
        
        # 메인 레이아웃에 좌우 컨테이너 추가
        h_layout.addWidget(left_container)
        h_layout.addWidget(right_container)
        
        # 가상 키보드
        self.keyboard = VirtualKeyboard(self)
        self.keyboard.setFixedSize(1000, 500)
        self.keyboard.move(
            (Config.DISPLAY_WIDTH - 1000) // 2,
            Config.DISPLAY_HEIGHT - 500
        )
        
        # 입력 필드 포커스 이벤트
        # self.name_input.focusInEvent = lambda e: self.keyboard.switch_input(self.name_input)
        # self.birth_input.focusInEvent = lambda e: self.keyboard.switch_input(self.birth_input)
        self.keyboard.show()

    
    def start_drag(self, event):
        if self.parent.current_image is not None:
            self.drag_start_pos = event.pos()
    
    def drag(self, event):
        if self.drag_start_pos and self.parent.current_image is not None:
            delta = event.pos() - self.drag_start_pos
            
            # 현재 줌 레벨에서의 이미지 크기 계산
            zoom = self.zoom_slider.value() / 10.0
            current_image = self.parent.current_image
            img_height, img_width = current_image.shape[:2]
            
            # 이미지 크기와 프리뷰 프레임의 비율 계산
            frame_ratio = self.preview_frame.width() / self.preview_frame.height()
            image_ratio = img_width / img_height
            
            if image_ratio > frame_ratio:
                # 이미지가 더 넓은 경우
                display_width = self.preview_frame.width() * zoom
                display_height = display_width / image_ratio
            else:
                # 이미지가 더 높은 경우
                display_height = self.preview_frame.height() * zoom
                display_width = display_height * image_ratio
            
            # 드래그 범위 제한
            if display_width > self.preview_frame.width() or display_height > self.preview_frame.height():
                self.image_position["x"] += delta.x()
                self.image_position["y"] += delta.y()
                
                # 최대 이동 범위 계산
                max_x = (display_width - self.preview_frame.width()) / 2
                max_y = (display_height - self.preview_frame.height()) / 2
                
                # 이동 범위 제한
                self.image_position["x"] = max(-max_x, min(max_x, self.image_position["x"]))
                self.image_position["y"] = max(-max_y, min(max_y, self.image_position["y"]))
                
                self.update_preview()
            
            self.drag_start_pos = event.pos()
    
    def stop_drag(self, event):
        self.drag_start_pos = None
    
    def rotate_image(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.image_position = {"x": 0, "y": 0}
        self.update_preview()
    
    def update_preview(self):
        if self.parent.current_image is not None:
            image = self.parent.current_image.copy()
            
            # OpenCV BGR -> RGB 변환
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_height, img_width = image_rgb.shape[:2]
            
            # 회전 적용
            if self.rotation_angle != 0:
                matrix = cv2.getRotationMatrix2D((img_width/2, img_height/2), self.rotation_angle, 1)
                image_rgb = cv2.warpAffine(image_rgb, matrix, (img_width, img_height))
            
            # 프리뷰 프레임과 이미지 비율 계산
            frame_ratio = self.preview_frame.width() / self.preview_frame.height()
            image_ratio = img_width / img_height
            
            # 줌 레벨 계산
            zoom = self.zoom_slider.value() / 10.0
            
            # 이미지 크기 계산
            if image_ratio > frame_ratio:
                # 이미지가 더 넓은 경우
                display_width = self.preview_frame.width() * zoom
                display_height = display_width / image_ratio
            else:
                # 이미지가 더 높은 경우
                display_height = self.preview_frame.height() * zoom
                display_width = display_height * image_ratio
            
            # 이미지 리사이즈
            image_rgb = cv2.resize(image_rgb, (int(display_width), int(display_height)))
            
            # 캔버스 생성 (프리뷰 프레임 크기)
            canvas = np.full((self.preview_frame.height(), self.preview_frame.width(), 3), 255, dtype=np.uint8)
            
            # 이미지 중앙 정렬 및 위치 조정
            x_offset = int((self.preview_frame.width() - display_width) / 2 + self.image_position["x"])
            y_offset = int((self.preview_frame.height() - display_height) / 2 + self.image_position["y"])
            
            # 이미지를 캔버스에 붙이기 (범위 체크)
            y1 = max(0, y_offset)
            y2 = min(self.preview_frame.height(), y_offset + image_rgb.shape[0])
            x1 = max(0, x_offset)
            x2 = min(self.preview_frame.width(), x_offset + image_rgb.shape[1])
            
            if y2 > y1 and x2 > x1:
                img_y1 = max(0, -y_offset)
                img_y2 = img_y1 + (y2 - y1)
                img_x1 = max(0, -x_offset)
                img_x2 = img_x1 + (x2 - x1)
                
                canvas[y1:y2, x1:x2] = image_rgb[img_y1:img_y2, img_x1:img_x2]
            
            # QImage로 변환 및 표시
            height, width = canvas.shape[:2]
            bytes_per_line = 3 * width
            qt_image = QImage(canvas.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            self.preview_label.setPixmap(QPixmap.fromImage(qt_image))
            
    def get_cropped_image(self):
        """현재 preview에 보이는 영역을 그대로 크롭하여 반환"""
        if self.parent.current_image is not None:
            # 원본 이미지 복사
            image = self.parent.current_image.copy()
            
            # BGR을 RGB로 변환
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_height, img_width = image_rgb.shape[:2]
            
            # 회전 적용
            if self.rotation_angle != 0:
                matrix = cv2.getRotationMatrix2D((img_width/2, img_height/2), self.rotation_angle, 1)
                image_rgb = cv2.warpAffine(image_rgb, matrix, (img_width, img_height))
            
            # preview 프레임과 이미지의 비율 계산
            frame_ratio = self.preview_frame.width() / self.preview_frame.height()
            image_ratio = img_width / img_height
            
            # 현재 줌 레벨 가져오기
            zoom = self.zoom_slider.value() / 10.0
            
            # preview에서의 이미지 크기 계산
            if image_ratio > frame_ratio:
                # 이미지가 더 넓은 경우
                display_width = self.preview_frame.width() * zoom
                display_height = display_width / image_ratio
            else:
                # 이미지가 더 높은 경우
                display_height = self.preview_frame.height() * zoom
                display_width = display_height * image_ratio
            
            # 이미지 리사이즈 (현재 줌 레벨 적용)
            resized = cv2.resize(image_rgb, (int(display_width), int(display_height)))
            
            # preview의 중심점과 현재 이동 offset을 고려한 크롭 영역 계산
            x_center = (display_width / 2) - self.image_position["x"]
            y_center = (display_height / 2) - self.image_position["y"]
            
            # preview 프레임 크기만큼의 영역을 크롭
            x1 = int(x_center - self.preview_frame.width() / 2)
            y1 = int(y_center - self.preview_frame.height() / 2)
            x2 = int(x_center + self.preview_frame.width() / 2)
            y2 = int(y_center + self.preview_frame.height() / 2)
            
            # 크롭 범위가 이미지를 벗어나지 않도록 조정
            x1 = max(0, min(x1, resized.shape[1]))
            y1 = max(0, min(y1, resized.shape[0]))
            x2 = max(0, min(x2, resized.shape[1]))
            y2 = max(0, min(y2, resized.shape[0]))
            
            # 이미지 크롭
            cropped = resized[y1:y2, x1:x2]
            
            # OpenCV 이미지를 PIL Image로 변환
            image_pil = Image.fromarray(cropped)
            
            # 프린터 출력 해상도에 맞게 최종 크기 조정
            final_width = int(Config.PHOTO_WIDTH * Config.PRINTER_DPI / 25.4)
            final_height = int(Config.PHOTO_HEIGHT * Config.PRINTER_DPI / 25.4)
            
            # 최종 크기로 리사이즈
            image_pil = image_pil.resize((final_width, final_height), Image.Resampling.LANCZOS)
            
            return image_pil
            
        return None


    def process_and_print(self):
        """카드 발급 처리"""
        name = self.name_input.text().strip()
        birthdate = self.birth_input.text().strip()
        
        print("\n=== 카드 발급 프로세스 시작 ===")
        print(f"입력된 이름: {name}")
        print(f"입력된 생년월일: {birthdate}")
        
        if not name or not birthdate:
            print("입력값 누락")
            QMessageBox.critical(self, "오류", "모든 필드를 입력해주세요.")
            return
        
        print("중복 체크 시작...")
        is_duplicate = ExcelManager.check_duplicate(name, birthdate)
        print(f"중복 체크 결과: {is_duplicate}")
        
        if is_duplicate:
            print("중복 발견!")
            QMessageBox.critical(self, "오류", "이미 발급된 기록이 있습니다.")
            return
        
        print("중복 없음, 발급 진행...")
        cropped_image = self.get_cropped_image()
        if cropped_image:
            print("이미지 크롭 성공")
            if ExcelManager.save_visitor_info(name, birthdate):
                print("방문자 정보 저장 성공")
                success, _ = print_honorary_citizen_card(name, birthdate, cropped_image)
                if success:
                    print("카드 발급 성공")
                    QMessageBox.information(self, "안내", "카드가 발급되었습니다.")
                    self.reset_form()
                    self.parent.show_frame("MainScreen")
                else:
                    print("카드 발급 실패")
                    QMessageBox.critical(self, "오류", "카드 발급 중 오류가 발생했습니다.")
            else:
                print("방문자 정보 저장 실패")
                QMessageBox.critical(self, "오류", "데이터 저장 중 문제가 발생했습니다.")
    
    def reset_form(self):
        """폼 초기화"""
        self.name_input.clear()
        self.birth_input.clear()
        self.rotation_angle = 0
        self.zoom_slider.setValue(10)
        self.image_position = {"x": 0, "y": 0}
        self.update_preview()
        self.keyboard.hide()
        

    
    def showEvent(self, event):
        super().showEvent(event)
        self.keyboard.switch_input(self.name_input)  # 초기 입력 대상 설정
        self.keyboard.show()  # 키보드 표시
        self.update_preview()
        
    def hideEvent(self, event):
        """화면이 숨겨질 때"""
        super().hideEvent(event)
        self.keyboard.hide()
        