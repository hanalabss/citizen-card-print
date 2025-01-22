import sys
import os
import logging
import shutil
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from config import Config

# 로깅 설정
logging.basicConfig(
    filename='visitor_card.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def setup_resources():
    """리소스 폴더 설정"""
    try:
        if getattr(sys, 'frozen', False):
            # PyInstaller로 패키징된 경우
            base_path = sys._MEIPASS
            exe_dir = os.path.dirname(sys.executable)
            
            # _internal/resources 경로
            internal_resources = os.path.join(base_path, 'resources')
            
            # 실행 파일과 같은 레벨의 resources 경로
            target_resources = os.path.join(exe_dir, 'resources')
            
            logging.info(f"Internal resources path: {internal_resources}")
            logging.info(f"Target resources path: {target_resources}")
            
            # resources 폴더가 이미 있는지 확인
            if not os.path.exists(target_resources) and os.path.exists(internal_resources):
                logging.info("Copying resources folder to executable directory...")
                # 폴더 전체를 복사
                shutil.copytree(internal_resources, target_resources)
                logging.info("Resources folder copied successfully")
                
    except Exception as e:
        logging.error(f"리소스 설정 중 오류 발생: {e}", exc_info=True)

def main():
    try:
        logging.info("Starting application...")
        
        # 리소스 설정 (프로그램 시작 시 한 번만 실행)
        setup_resources()
        
        # 앱 생성
        app = QApplication(sys.argv)
        
        # DPI 설정
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # MainWindow import는 QApplication 생성 후에
        from app import MainWindow
        
        # 스타일시트 로드
        try:
            # 실행 파일과 같은 레벨의 resources 폴더에서 스타일시트 로드
            if getattr(sys, 'frozen', False):
                style_path = os.path.join(os.path.dirname(sys.executable), 'resources', 'styles', 'style.qss')
            else:
                style_path = os.path.join(Config.RESOURCES_DIR, 'styles', 'style.qss')
                
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    app.setStyleSheet(f.read())
                logging.info(f"Stylesheet loaded from: {style_path}")
            else:
                logging.warning(f"Stylesheet not found at: {style_path}")
        except Exception as e:
            logging.warning(f"Failed to load stylesheet: {e}")
        
        # 메인 윈도우 생성
        window = MainWindow()
        window.setWindowTitle(Config.APP_TITLE)
        window.showFullScreen()
        
        logging.info("Application window created and shown")
        
        # 이벤트 루프 시작
        sys.exit(app.exec())
        
    except Exception as e:
        error_msg = f"프로그램 실행 중 오류가 발생했습니다:\n{str(e)}"
        logging.error(error_msg, exc_info=True)
        
        # 에러 로그 파일에 상세 정보 기록
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n")
            import traceback
            f.write(f"Traceback:\n{traceback.format_exc()}\n")

if __name__ == "__main__":
    main()