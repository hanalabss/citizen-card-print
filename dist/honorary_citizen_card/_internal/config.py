import os


class Config:
    # 디스플레이 설정
    DISPLAY_WIDTH = 1920
    DISPLAY_HEIGHT = 1080
    WINDOW_SIZE = f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}"
    
    # 앱 설정
    APP_TITLE = "구례군 명예군민증 발급 시스템"
    
    # 바탕화면 경로 가져오기
    try:
        DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
    except:
        DESKTOP_PATH = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    
    # 파일 경로
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(DESKTOP_PATH, 'GureyeCard')  # 바탕화면에 폴더 생성
    EXCEL_PATH = os.path.join(DATA_DIR, 'visitors.xlsx')
    
    # 카메라 설정 - 16:9 비율 최적화
    CAMERA_WIDTH = 1920
    CAMERA_HEIGHT = 1080
    CAMERA_FPS = 30
    
    # 프리뷰 크기 설정
    PREVIEW_WIDTH = 960
    PREVIEW_HEIGHT = 540
    
    # 카드 크기 (mm)
    CARD_WIDTH = 58
    CARD_HEIGHT = 90
    
    # UI 설정
    TITLE_FONT_SIZE = 36
    BUTTON_FONT_SIZE = 24
    LABEL_FONT_SIZE = 20
    
    # 리소스 경로 추가
    RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
    OUTPUT_DIR = os.path.join(DATA_DIR, 'output')  # 바탕화면의 폴더 안에 output 폴더
    PRINTER_DPI = 300
    
    PHOTO_WIDTH = 26
    PHOTO_HEIGHT = 36
    
    # 초기 폴더 생성
    @classmethod
    def initialize_directories(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)