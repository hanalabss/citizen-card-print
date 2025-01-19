import os

class Config:
    # 앱 설정
    APP_TITLE = "구례군 명예군민증 발급 시스템"
    WINDOW_SIZE = "800x600"
    
    # 파일 경로
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    EXCEL_PATH = os.path.join(DATA_DIR, 'visitors.xlsx')
    
    # 카메라 설정
    CAMERA_WIDTH = 1920
    CAMERA_HEIGHT = 1080
    CAMERA_FPS = 30
    
    # 카드 크기 (mm)
    CARD_WIDTH = 58
    CARD_HEIGHT = 90