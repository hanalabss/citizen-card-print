import tkinter as tk
from tkinter import ttk
from src.screens.photo_screen import PhotoFrame
from src.screens.info_screen import InfoFrame
from src.config import Config

class VisitorCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title(Config.APP_TITLE)
        
        # 전체화면으로 설정
        self.root.attributes('-fullscreen', True)
        # ESC 키로 전체화면 종료
        self.root.bind('<Escape>', lambda e: self.on_closing())
        
        # 전역 변수 초기화
        self.current_image = None
        self.camera = None
        
        # 메인 컨테이너
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Grid 설정으로 프레임이 전체 공간을 사용하도록 함
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # 프레임 생성
        self.frames = {}
        frame_classes = {
            "PhotoFrame": PhotoFrame,
            "InfoFrame": InfoFrame
        }
        
        for name, F in frame_classes.items():
            frame = F(self.main_container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # 초기 화면 설정
        self.show_frame("PhotoFrame")
        
        # 창이 닫힐 때 카메라 해제
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_frame(self, frame_name):
        """화면 전환 함수"""
        frame = self.frames[frame_name]
        frame.tkraise()
    
    def on_closing(self):
        """프로그램 종료 시 카메라 해제"""
        if self.camera is not None:
            self.camera.release()
        self.root.destroy()