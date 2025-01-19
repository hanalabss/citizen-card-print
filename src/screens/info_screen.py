import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
from src.utils.excel import ExcelManager

class InfoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # 전체 레이아웃 설정
        self.grid_rowconfigure(0, weight=0)  # 프리뷰 영역
        self.grid_rowconfigure(1, weight=0)  # 입력 폼
        self.grid_columnconfigure(0, weight=1)
        
        # 미리보기 영역 추가
        preview_frame = ttk.Frame(self, style='Main.TFrame')
        preview_frame.grid(row=0, column=0, pady=10, sticky='n')
        
        # 이미지를 표시할 캔버스 생성 - 배경색 추가
        self.preview_canvas = tk.Canvas(preview_frame, 
                                      width=300, height=400,
                                      bg='white',
                                      highlightthickness=1, 
                                      highlightbackground="gray")
        self.preview_canvas.pack(padx=10, pady=10)
        
        # 마우스 이벤트 바인딩
        self.preview_canvas.bind("<ButtonPress-1>", self.start_drag)
        self.preview_canvas.bind("<B1-Motion>", self.drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.stop_drag)
        
        # 드래그 관련 변수
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.image_position = {"x": 0, "y": 0}  # 이미지 위치 저장
        
        # 회전 각도 초기화
        self.rotation_angle = 0
        
        # 줌 컨트롤 프레임
        zoom_frame = ttk.Frame(preview_frame, style='Main.TFrame')
        zoom_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(zoom_frame, text="확대/축소:", style='TLabel').pack(side=tk.LEFT, padx=5)
        self.zoom_scale = ttk.Scale(zoom_frame, 
                                  from_=1.0, to=3.0,
                                  orient='horizontal',
                                  command=self.update_preview,
                                  length=200)
        self.zoom_scale.set(1.0)
        self.zoom_scale.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        
        # 회전 버튼
        ttk.Button(preview_frame, 
                  text="회전",
                  style='TButton',
                  command=self.rotate_image).pack(pady=5)
        
        # 입력 필드와 버튼 영역 추가
        form_frame = ttk.Frame(self, style='Main.TFrame')
        form_frame.grid(row=1, column=0, sticky='n')

        # 제목 추가
        title_frame = ttk.Frame(form_frame, style='Main.TFrame')
        title_frame.pack(pady=20)

        # 입력 필드
        fields_container = ttk.Frame(form_frame, padding="20 10", style='Main.TFrame')
        fields_container.pack(fill='x', padx=50)

        # 이름 입력
        name_frame = ttk.Frame(fields_container, style='Main.TFrame')
        name_frame.pack(fill='x', pady=15)
        ttk.Label(name_frame, text="이름", 
                 style='Header.TLabel').pack(anchor='w', pady=(0,5))
        self.name_entry = ttk.Entry(name_frame, 
                                  font=('Pretendard', 18),
                                  width=25)
        self.name_entry.pack(fill='x', ipady=8)
        
        # 생년월일 입력
        birth_frame = ttk.Frame(fields_container, style='Main.TFrame')
        birth_frame.pack(fill='x', pady=15)
        ttk.Label(birth_frame, text="생년월일", 
                 style='Header.TLabel').pack(anchor='w', pady=(0,5))
        birth_hint = ttk.Label(birth_frame, text="예시) 19901231", 
                            font=('Pretendard', 14), foreground='gray')
        birth_hint.pack(anchor='w', pady=(0,5))
        self.birth_entry = ttk.Entry(birth_frame, 
                                   font=('Pretendard', 18),
                                   width=25)
        self.birth_entry.pack(fill='x', ipady=8)
        
        # 버튼 컨테이너
        button_container = ttk.Frame(form_frame, style='Main.TFrame')
        button_container.pack(pady=30)

        # 모든 버튼을 한 줄로 배치
        button_width = 20  # 각 버튼의 너비
        button_row = ttk.Frame(button_container, style='Main.TFrame')
        button_row.pack()
        
        ttk.Button(button_row, 
            text="카드 발급", 
            style='Action.TButton',
            command=self.process_and_print,
            width=button_width).pack(side='left', padx=10)
                
        ttk.Button(button_row, 
                  text="다시 찍기", 
                  style='Action.TButton',
                  command=lambda: self.controller.show_frame("PhotoFrame"),
                  width=button_width).pack(side='left', padx=10)
                  
        ttk.Button(button_row, 
                  text="초기화", 
                  style='Action.TButton',
                  command=self.reset_form,
                  width=button_width).pack(side='left', padx=10)
                  


        # 페이지 진입 시 이미지 업데이트
        self.bind("<Visibility>", self.on_visibility)
        
        # 현재 이미지 변수 초기화
        self.current_image = None
        self.current_photo = None

    def on_resize(self, scale):
        """크기 조정 이벤트 처리"""
        new_width = int(300 * scale)
        new_height = int(400 * scale)
        self.preview_canvas.config(width=new_width, height=new_height)

        # 입력 필드 및 버튼 크기 조정
        font_size = int(18 * scale)
        self.name_entry.config(font=('Pretendard', font_size))
        self.birth_entry.config(font=('Pretendard', font_size))
    
    def on_visibility(self, event):
        """페이지가 보일 때 실행"""
        if str(event.state) == 'VisibilityUnobscured':
            print("Debug: InfoFrame became visible")
            if hasattr(self.controller, 'current_image'):
                print("Debug: current_image exists")
                if self.controller.current_image is not None:
                    print("Debug: current_image is not None")
                    print("Debug: Image shape:", self.controller.current_image.shape)
            self.reset_image_settings()
            self.update_preview()

    def _init_preview(self):
        """이미지 프리뷰 초기화 및 업데이트"""
        if hasattr(self.controller, 'current_image') and self.controller.current_image is not None:
            # 이미지 설정 초기화
            self.reset_image_settings()
            # 캔버스 초기화
            self.preview_canvas.delete("all")
            
            # OpenCV 이미지를 PIL 이미지로 변환
            image = cv2.cvtColor(self.controller.current_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            
            # 미리보기 크기 조정
            base_width = 300
            base_height = 400
            
            # 이미지 비율 계산
            img_ratio = image.width / image.height
            base_ratio = base_width / base_height
            
            if img_ratio > base_ratio:
                new_width = int(base_height * img_ratio)
                new_height = base_height
            else:
                new_width = base_width
                new_height = int(base_width / img_ratio)
            
            # 이미지 리사이즈
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 현재 이미지 저장
            self.current_image = image
            self.current_photo = ImageTk.PhotoImage(image)
            
            # 이미지를 캔버스 중앙에 배치
            x = base_width/2 - new_width/2
            y = base_height/2 - new_height/2
            self.preview_canvas.create_image(x, y, image=self.current_photo, anchor="nw")
            
            # 캔버스 강제 업데이트
            self.preview_canvas.update()
            
    def reset_image_settings(self):
        """이미지 설정 초기화"""
        self.image_position = {"x": 0, "y": 0}
        self.rotation_angle = 0
        self.zoom_scale.set(1.0)
    
    def start_drag(self, event):
        """드래그 시작"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["item"] = self.preview_canvas.find_closest(event.x, event.y)
    
    def drag(self, event):
        """드래그 중"""
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            self.image_position["x"] += dx
            self.image_position["y"] += dy
            
            self.preview_canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
    
    def stop_drag(self, event):
        """드래그 종료"""
        self.drag_data["item"] = None
    
    def update_preview(self, event=None):
        """이미지 프리뷰 업데이트"""
        if hasattr(self.controller, 'current_image') and self.controller.current_image is not None:
            print("Updating preview...")  # 디버깅용
            
            # OpenCV 이미지를 PIL 이미지로 변환
            image = cv2.cvtColor(self.controller.current_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            
            # 회전 적용
            if self.rotation_angle != 0:
                image = image.rotate(self.rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)
            
            # 줌 적용
            zoom = self.zoom_scale.get()
            
            # 미리보기 크기 조정 (초기 크기 설정)
            base_width = 300
            base_height = 400
            
            # 이미지 비율 계산
            img_ratio = image.width / image.height
            base_ratio = base_width / base_height
            
            if img_ratio > base_ratio:
                # 이미지가 더 넓은 경우
                new_width = int(base_height * img_ratio)
                new_height = base_height
            else:
                # 이미지가 더 높은 경우
                new_width = base_width
                new_height = int(base_width / img_ratio)
            
            # 줌이 적용된 크기 계산
            zoom_width = int(new_width * zoom)
            zoom_height = int(new_height * zoom)
            
            # 이미지 리사이즈
            image = image.resize((zoom_width, zoom_height), Image.Resampling.LANCZOS)
            
            # 현재 이미지 저장
            self.current_image = image
            
            # PhotoImage로 변환
            self.current_photo = ImageTk.PhotoImage(image)
            
            # 캔버스 크기 설정
            self.preview_canvas.config(width=base_width, height=base_height)
            
            # 기존 이미지 삭제
            self.preview_canvas.delete("all")
            
            # 새 이미지 추가 (드래그 위치 반영)
            x = base_width/2 - zoom_width/2 + self.image_position["x"]
            y = base_height/2 - zoom_height/2 + self.image_position["y"]
            self.preview_canvas.create_image(x, y, image=self.current_photo, anchor="nw")
            
            print(f"Image placed at: ({x}, {y})")  # 디버깅용
        else:
            print("No image available for preview")  # 디버깅용
    
    def rotate_image(self):
        """이미지 90도 회전"""
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.image_position = {"x": 0, "y": 0}  # 회전 시 위치 초기화
        self.update_preview()
    
    def reset_form(self):
        """입력 폼 초기화"""
        self.name_entry.delete(0, tk.END)
        self.birth_entry.delete(0, tk.END)
        self.reset_image_settings()
        self.update_preview()
    
    def get_cropped_image(self):
        """현재 보이는 영역의 이미지만 크롭하여 ID카드 크기로 반환"""
        if self.current_image:
            # 현재 캔버스 크기
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # 보이는 영역 계산
            left = max(0, -self.image_position["x"])
            top = max(0, -self.image_position["y"])
            right = min(self.current_image.width, canvas_width - self.image_position["x"])
            bottom = min(self.current_image.height, canvas_height - self.image_position["y"])
            
            # 이미지 크롭
            cropped = self.current_image.crop((left, top, right, bottom))
            
            # ID 카드 크기로 리사이즈 (58mm x 90mm, 300DPI 기준)
            id_width = 685  # 58mm in pixels at 300DPI
            id_height = 1063  # 90mm in pixels at 300DPI
            return cropped.resize((id_width, id_height), Image.Resampling.LANCZOS)
        return None
    
    def process_and_print(self):
        """정보 처리 및 카드 발급"""
        name = self.name_entry.get().strip()
        birthdate = self.birth_entry.get().strip()
        
        if not name or not birthdate:
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return
            
        if ExcelManager.check_duplicate(name, birthdate):
            messagebox.showerror("오류", "이미 등록된 방문자입니다.")
            return
        
        # 크롭된 이미지 가져오기
        cropped_image = self.get_cropped_image()
        if cropped_image:
            if ExcelManager.save_visitor_info(name, birthdate):
                # 카드 발급 처리
                self.print_card()
                # 입력 필드 초기화
                self.reset_form()
                # 메인 화면으로 자동 복귀
                self.controller.show_frame("PhotoFrame")
            else:
                messagebox.showerror("오류", "데이터 저장 중 문제가 발생했습니다.")
    
    def print_card(self):
        """카드 발급 처리"""
        messagebox.showinfo("안내", "카드가 발급되었습니다.")