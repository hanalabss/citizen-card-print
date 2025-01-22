import pandas as pd
from datetime import datetime
from config import Config
import os

class ExcelManager:
    @staticmethod
    def check_duplicate(name, birthdate):
        """중복 체크 함수"""
        try:
            # 디렉토리 초기화
            Config.initialize_directories()
            
            if os.path.exists(Config.EXCEL_PATH):
                # 엑셀 파일 읽기 (인코딩 명시)
                df = pd.read_excel(Config.EXCEL_PATH, dtype={'이름': str, '생년월일': str})
                
                # 입력값 정규화
                name = name.strip()
                birthdate = birthdate.strip()
                
                # DataFrame의 값들도 정규화
                df['이름'] = df['이름'].str.strip()
                df['생년월일'] = df['생년월일'].str.strip()
                
                # 각 행 검사
                for index, row in df.iterrows():
                    if row['이름'] == name and row['생년월일'] == birthdate:
                        return True
                return False
                
            return False
            
        except Exception as e:
            return False
    
    @staticmethod
    def save_visitor_info(name, birthdate):
        """방문자 정보 저장"""
        try:
            # 디렉토리 초기화
            Config.initialize_directories()
            
            new_data = pd.DataFrame({
                '이름': [name],
                '생년월일': [birthdate],
                '등록일시': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            })
            
            if os.path.exists(Config.EXCEL_PATH):
                df = pd.read_excel(Config.EXCEL_PATH)
                df = pd.concat([df, new_data], ignore_index=True)
            else:
                df = new_data
            
            # 엑셀 파일 저장
            df.to_excel(Config.EXCEL_PATH, index=False)
            return True
        except Exception as e:
            return False