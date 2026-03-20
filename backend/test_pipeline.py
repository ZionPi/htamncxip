import os
import sys
import time
import traceback
from PIL import Image
from paddleocr import PaddleOCR

# --- 1. 修正后的导入逻辑 ---
print("📦 Loading RapidLatexOCR...")
try:
    # 根据你的 debug 信息，类名是 LaTeXOCR
    from rapid_latex_ocr import LaTeXOCR
except ImportError:
    try:
        # 备选：有时候在 main 里
        from rapid_latex_ocr.main import LaTeXOCR
    except ImportError as e:
        print(f"❌ Import Failed: {e}")
        sys.exit(1)

# --- 2. 初始化引擎 ---
print("   🚀 Initializing engines...")

# PaddleOCR
ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)

# RapidLatexOCR
try:
    # 初始化
    latex_engine = LaTeXOCR()
except Exception as e:
    print(f"❌ RapidLatexOCR Init Failed: {e}")
    sys.exit(1)

def recognize_mixed(image_path):
    print(f"\n🔍 Processing: {image_path}")
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return

    # --- A. 公式识别 ---
    print("   [1/2] Running Formula Rec...")
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        
        start = time.time()
        # 识别
        res, elapse = latex_engine(data)
        
        print("\n" + "="*30)
        print("🧮 [LaTeX Result]:")
        print(res)
        print(f"   (Time: {elapse:.4f}s)")
        print("="*30 + "\n")
        
    except Exception as e:
        print(f"❌ Latex Error: {e}")
        traceback.print_exc()
    
    # --- B. 文本识别 ---
    print("   [2/2] Running Text Rec...")
    try:
        result = ocr_engine.ocr(image_path, cls=True)
        print("📝 [PaddleOCR Result]:")
        if result and result[0]:
            for line in result[0]:
                print(f"   {line[1][0]}")
        else:
            print("   (No text detected)")
    except Exception as e:
        print(f"❌ PaddleOCR Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        recognize_mixed(sys.argv[1])
    else:
        print("❌ Usage: python backend/test_pipeline.py <image_path>")