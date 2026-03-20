import time
import uvicorn
import io
import os
import sys
import numpy as np
import cv2
import re
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from PIL import Image

# --- 1. 导入 RapidLatexOCR ---
print("📦 Loading RapidLatexOCR...")
try:
    from rapid_latex_ocr import LaTeXOCR
except ImportError:
    try:
        from rapid_latex_ocr.main import LaTeXOCR
    except ImportError:
        print("❌ Error: Could not import LaTeXOCR.")
        sys.exit(1)

# --- 2. 初始化 APP ---
app = FastAPI(title="htamncxip Backend", description="OCR with Smart Chinese-Masking")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. 全局加载模型 ---
print("🚀 Loading Models...")

# A. 文本识别 (PaddleOCR)
ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)

# B. 公式识别 (RapidLatexOCR)
latex_engine = LaTeXOCR()

print("✅ Models Loaded!")

def contains_chinese(text):
    """判断字符串是否包含中文字符"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

@app.get("/")
def home():
    return {"status": "running", "service": "htamncxip"}

@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...), 
    mode: str = Form("smart")
):
    start_time = time.time()
    
    # 1. 读取图片
    image_bytes = await file.read()
    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(image_pil) 
    
    response = {
        "latex": "",
        "text": [],
        "debug_info": "",
        "time_cost": 0.0
    }

    try:
        # --- 步骤 1: 全图文本识别 (PaddleOCR) ---
        ocr_result = ocr_engine.ocr(img_np, cls=True)
        
        boxes_to_mask = []
        found_texts = []
        
        if ocr_result and ocr_result[0]:
            for line in ocr_result[0]:
                box = line[0]
                txt = line[1][0]
                score = line[1][1]
                
                # 记录所有识别出的文本
                # (我们可以选择不返回包含中文的文本，或者分开返回，这里先都返回)
                found_texts.append(txt)
                
                # --- 核心逻辑改进 ---
                # 只有当识别出的文本包含中文时，才认为是“干扰项”并涂抹
                # 如果是纯英文/符号，很可能是公式的一部分被 Paddle 误读了，必须保留！
                if contains_chinese(txt):
                    boxes_to_mask.append(box)
                else:
                    # 可选：如果 score 很低，也可能是把公式误读成了乱码，不涂抹
                    pass
                
        response["text"] = found_texts
        
        # --- 步骤 2: 智能涂抹 ---
        img_for_latex = img_np.copy()
        
        if len(boxes_to_mask) > 0:
            for box in boxes_to_mask:
                pts = np.array(box, np.int32)
                pts = pts.reshape((-1, 1, 2))
                # 涂白中文区域，消除对公式模型的干扰
                cv2.fillPoly(img_for_latex, [pts], color=(255, 255, 255))
        
        # --- 步骤 3: 识别公式 (RapidLatexOCR) ---
        # 此时 img_for_latex 上：
        # 1. 中文区域变成了白色
        # 2. 公式区域完好无损 (因为 Paddle 识别出的公式字符串不含中文，所以没被涂抹)
        
        is_success, buffer = cv2.imencode(".png", img_for_latex)
        if is_success:
            try:
                latex_bytes = buffer.tobytes()
                res, _ = latex_engine(latex_bytes)
                response["latex"] = res
            except Exception as e:
                print(f"Latex Error: {e}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    response["time_cost"] = round(time.time() - start_time, 4)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8128)