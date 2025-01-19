import pandas as pd
from datetime import datetime
from src.config import Config
import os

class ExcelManager:
    @staticmethod
    def check_duplicate(name, birthdate):
        """중복 체크 함수"""
        try:
            if os.path.exists(Config.EXCEL_PATH):
                df = pd.read_excel(Config.EXCEL_PATH)
                return ((df['이름'] == name) & (df['생년월일'] == birthdate)).any()
            return False
        except Exception as e:
            print(f"중복 체크 오류: {e}")
            return False
    
    @staticmethod
    def save_visitor_info(name, birthdate):
        """방문자 정보 저장"""
        try:
            new_data = pd.DataFrame({
                '이름': [name],
                '생년월일': [birthdate],
                '등록일시': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            })
            
            if os.path.exists(Config.EXCEL_PATH):
                df = pd.read_excel(Config.EXCEL_PATH)
                df = pd.concat([df, new_data], ignore_index=True)
            else:
                # 디렉토리가 없으면 생성
                os.makedirs(os.path.dirname(Config.EXCEL_PATH), exist_ok=True)
                df = new_data
                
            df.to_excel(Config.EXCEL_PATH, index=False)
            return True
        except Exception as e:
            print(f"데이터 저장 오류: {e}")
            return False