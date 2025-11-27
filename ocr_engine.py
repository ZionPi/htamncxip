import numpy as np
import cv2
import re
from paddleocr import PaddleOCR
# 兼容导入
try:
    from rapid_latex_ocr import LaTeXOCR
except ImportError:
    from rapid_latex_ocr.main import LaTeXOCR

class OcrHandler:
    def __init__(self):
        print("🚀 Loading OCR Models...")
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        self.latex = LaTeXOCR()
        print("✅ Models Loaded")

    def contains_chinese(self, text):
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False

    def run(self, img_pil):
        # 转 numpy
        img_np = np.array(img_pil.convert("RGB"))
        
        # 1. Paddle 识别
        result = self.ocr.ocr(img_np, cls=True)
        found_texts = []
        boxes_to_mask = []
        
        if result and result[0]:
            for line in result[0]:
                box = line[0]
                txt = line[1][0]
                found_texts.append(txt)
                if self.contains_chinese(txt):
                    boxes_to_mask.append(box)
        
        # 2. 涂抹
        img_for_latex = img_np.copy()
        for box in boxes_to_mask:
            pts = np.array(box, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(img_for_latex, [pts], (255, 255, 255))
            
        # 3. Latex
        latex_code = ""
        is_success, buffer = cv2.imencode(".png", img_for_latex)
        if is_success:
            try:
                latex_code, _ = self.latex(buffer.tobytes())
            except Exception as e:
                latex_code = f"Error: {e}"
                
        return latex_code, found_texts