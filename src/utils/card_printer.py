from PIL import Image, ImageDraw, ImageFont, ImageWin
import os
from datetime import datetime
import win32print
import win32ui
from config import Config

class CardPrinter:
    def __init__(self):
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        # 프린터 설정값 (300DPI 기준)
        self.PRINTER_DPI = Config.PRINTER_DPI
        self.CARD_WIDTH_MM = Config.CARD_WIDTH
        self.CARD_HEIGHT_MM = Config.CARD_HEIGHT
        
        # mm를 dots로 변환
        self.width_dots = int(self.CARD_WIDTH_MM * self.PRINTER_DPI / 25.4)
        self.height_dots = int(self.CARD_HEIGHT_MM * self.PRINTER_DPI / 25.4)
        
        # 폰트 설정 - Windows 시스템 폰트 사용
        self.FONT_NAME = "malgun gothic"  # 맑은고딕
        self.FONT_SIZE = int(16 * self.PRINTER_DPI / 72)  # 11pt를 DPI에 맞게 변환
        
    def print_card(self, name, birthdate, photo):
        try:
            # 1. 빈 흰색 카드 생성
            card = Image.new('RGB', (self.width_dots, self.height_dots), 'white')
            
            # 카드와 사진의 실제 픽셀 크기 계산
            card_width_px = int(self.CARD_WIDTH_MM * self.PRINTER_DPI / 25.4)
            photo_width_px = int(Config.PHOTO_WIDTH * self.PRINTER_DPI / 25.4)
            photo_height_px = int(Config.PHOTO_HEIGHT * self.PRINTER_DPI / 25.4)
            
            # 사진 리사이즈
            photo = photo.resize((photo_width_px, photo_height_px), Image.Resampling.LANCZOS)
            
            # 정확한 중앙 위치 계산
            margin_x = (card_width_px - photo_width_px) // 2 - 20
            card_height_px = int(self.CARD_HEIGHT_MM * self.PRINTER_DPI / 25.4)
            image_y = int(card_height_px * 0.20)  # 이미지를 상단에서 약 20% 지점에 위치

            # 이미지 붙이기
            card.paste(photo, (margin_x, image_y))
            
            # 2. 텍스트 추가
            draw = ImageDraw.Draw(card)
            
            # 폰트 설정 - 직접 경로 사용
            font = None
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",      # 맑은 고딕 일반
                "C:/Windows/Fonts/MALGUN.TTF",      # 대문자로 시도
                "C:/Windows/Fonts/msgothic.ttc",    # MS Gothic
                "C:/Windows/Fonts/gulim.ttc"        # 굴림
            ]
            
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, self.FONT_SIZE)
                        print(f"폰트 로드 성공: {font_path}")
                        break
                except Exception as e:
                    print(f"폰트 로드 실패 ({font_path}): {str(e)}")
                    continue
            
            if font is None:
                print("모든 폰트 로드 실패, 기본 폰트 사용")
                font = ImageFont.load_default()
            
            # 텍스트 너비 계산
            name_bbox = draw.textbbox((0, 0), name, font=font)
            name_width = name_bbox[2] - name_bbox[0]
            
            birth_bbox = draw.textbbox((0, 0), birthdate, font=font)
            birth_width = birth_bbox[2] - birth_bbox[0]
            
            # 텍스트 x 좌표 계산
            name_x = (card_width_px - name_width) // 2 - 30
            birth_x = (card_width_px - birth_width) // 2 - 30
            
            # 텍스트 y 좌표 계산
            name_y = 260 + photo_height_px 
            birth_y = name_y + self.FONT_SIZE + 15
            
            # 텍스트 그리기
            draw.text((name_x, name_y), name, font=font, fill='black')
            # draw.text((birth_x, birth_y), birthdate, font=font, fill='black')
            
            # 3. 결과 이미지 저장
            output_filename = f"card_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
            card.save(output_path)
            
            # 4. 프린터 출력
            printer_name = win32print.GetDefaultPrinter()
            hprinter = win32print.OpenPrinter(printer_name)
            
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)
            
            hdc.StartDoc('명예군민증')
            hdc.StartPage()
            
            dib = ImageWin.Dib(card)
            dib.draw(hdc.GetHandleOutput(), 
                    (0, 0, self.width_dots, self.height_dots))
            
            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
            
            win32print.ClosePrinter(hprinter)
            
            return True, output_path
            
        except Exception as e:
            print(f"출력 오류: {str(e)}")
            return False, None

def print_honorary_citizen_card(name, birthdate, photo):
    """메인 출력 함수"""
    printer = CardPrinter()
    try:
        success, output_path = printer.print_card(name, birthdate, photo)
        
        if success:
            print(f"출력할 이름: {name}")
            print(f"출력할 생년월일: {birthdate}")
            print(f"카드가 성공적으로 출력되었습니다.")
            print(f"이미지 저장 경로: {output_path}")
            return True, output_path
        else:
            print("카드 출력에 실패했습니다.")
            return False, None
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False, None