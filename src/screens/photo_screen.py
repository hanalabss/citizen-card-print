import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import src.config as config

class PhotoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent, style='Main.TFrame')
        self.controller = controller
        
        # 초기 카메라 크기 설정
        self.default_width = config.Config.CAMERA_WIDTH
        self.default_height = config.Config.CAMERA_HEIGHT
        
        # 전체 레이아웃 구성
        self.grid_rowconfigure(0, weight=0)  # 제목
        self.grid_rowconfigure(1, weight=6)  # 카메라
        self.grid_rowconfigure(2, weight=1)  # 버튼
        self.grid_columnconfigure(0, weight=1)
        
        # 제목
        title_frame = ttk.Frame(self, style='Main.TFrame')
        title_frame.grid(row=0, column=0, pady=20)
        ttk.Label(title_frame, 
                 text="포토카드 촬영", 
                 style='Title.TLabel').pack()
        
        # 카메라 컨테이너
        camera_container = ttk.Frame(self, style='Main.TFrame')
        camera_container.grid(row=1, column=0, sticky="nsew", padx=40)
        camera_container.grid_rowconfigure(0, weight=1)
        camera_container.grid_columnconfigure(0, weight=1)
        
        # 카메라 프리뷰 캔버스
        self.preview_canvas = tk.Canvas(camera_container, 
                                      bg='black',
                                      highlightthickness=0)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        
        # 버튼 프레임
        button_frame = ttk.Frame(self, style='Main.TFrame')
        button_frame.grid(row=2, column=0, pady=20)
        
        # 촬영 버튼
        capture_btn = ttk.Button(button_frame, 
                               text="촬영하기", 
                               command=self.capture_photo,
                               style='Action.TButton',
                               width=20)
        capture_btn.pack(pady=10)
        
        self.start_camera()
        self.bind('<Configure>', self.on_resize)
    
    def start_camera(self):
        """카메라 시작"""
        self.controller.camera = cv2.VideoCapture(0)
        if self.controller.camera.isOpened():
            # Config에서 설정한 해상도 적용
            self.controller.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.Config.CAMERA_WIDTH)
            self.controller.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.Config.CAMERA_HEIGHT)
            
            # 실제 설정된 해상도 확인 (디버깅용)
            actual_width = self.controller.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.controller.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Camera resolution: {actual_width}x{actual_height}")
            
            self.update_camera()
        else:
            print("Error: Cannot open camera")
    
    def on_resize(self, event):
        """창 크기 변경 시 카메라 영역 크기 조정"""
        self.update_camera(force_resize=True)
    
    # photo_screen.py의 capture_photo 메서드 수정
    def capture_photo(self):
        """사진 촬영 후 자동으로 정보 입력 화면으로 이동"""
        if self.controller.camera is not None:
            ret, frame = self.controller.camera.read()
            if ret:
                self.controller.current_image = frame.copy()  # 이미지 복사본 저장
                print("Debug: Image captured")
                print("Debug: Image shape:", self.controller.current_image.shape)
                self.controller.show_frame("InfoFrame")
                # InfoFrame의 프리뷰 직접 초기화
                info_frame = self.controller.frames["InfoFrame"]
                info_frame.after(100, info_frame._init_preview)  # 약간의 지연을 주어 안정적으로 전환
    
    def update_camera(self, force_resize=False):
        """카메라 프레임 업데이트"""
        if self.controller.camera is not None and self.controller.camera.isOpened():
            ret, frame = self.controller.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 현재 카메라 프레임의 크기 얻기
                width = self.preview_canvas.winfo_width()
                height = self.preview_canvas.winfo_height()
                
                # 초기 실행시나 크기가 0일 때 기본 크기 사용
                if width <= 1 or height <= 1:
                    width = self.default_width
                    height = self.default_height
                
                # 비율 유지하면서 크기 조정
                image = Image.fromarray(frame)
                image_ratio = image.width / image.height
                frame_ratio = width / height
                
                if frame_ratio > image_ratio:
                    new_width = int(height * image_ratio)
                    new_height = height
                else:
                    new_width = width
                    new_height = int(width / image_ratio)
                
                # 최소 크기 보장
                new_width = max(new_width, 320)
                new_height = max(new_height, 240)
                
                try:
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image=image)
                    
                    # 이미지 중앙 정렬
                    x = (width - new_width) // 2
                    y = (height - new_height) // 2
                    
                    if not hasattr(self, 'camera_image_id'):
                        self.camera_image_id = self.preview_canvas.create_image(
                            x, y, image=photo, anchor="nw")
                    else:
                        self.preview_canvas.coords(self.camera_image_id, x, y)
                        self.preview_canvas.itemconfig(self.camera_image_id, image=photo)
                    
                    self.preview_canvas.image = photo
                    
                except Exception as e:
                    print(f"Error resizing image: {e}")
        
        if not force_resize:
            self.after(int(1000/config.Config.CAMERA_FPS), self.update_camera)