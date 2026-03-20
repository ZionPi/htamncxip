import sys
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QScreen, QPixmap, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout
import numpy as np

# 导入我们的 OCR 引擎
# 注意：这里为了 GUI 启动速度，我们在截图后才懒加载模型，或者在后台线程加载
# 这里为了演示简单，先占位，稍后集成
try:
    from paddleocr import PaddleOCR
    # rapid_latex_ocr 导入可能会慢，先不放这里
except ImportError:
    pass

class SnippingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(0.5) # 初始透明度
        
        # 获取屏幕截图
        screen = QApplication.primaryScreen()
        # 截取整个桌面
        self.original_pixmap = screen.grabWindow(0)
        
        # 窗口铺满全屏
        rect = screen.geometry()
        self.setGeometry(rect)
        
        self.begin = QPoint()
        self.end = QPoint()
        self.is_snipping = False
        
        # 显示截图作为背景（看起来像是静止了）
        self.setWindowOpacity(1.0) # 设回不透明，因为我们自己画图
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 1. 先把全屏截图画上去
        painter.drawPixmap(0, 0, self.original_pixmap)
        
        # 2. 画半透明黑色遮罩（模拟变暗）
        painter.setBrush(QColor(0, 0, 0, 100)) # 最后一个参数是 alpha (0-255)
        painter.drawRect(self.rect())
        
        # 3. 画选区（把选区部分的遮罩“挖掉”，即画回原图）
        if self.is_snipping:
            rect = QRect(self.begin, self.end).normalized()
            # 在选区位置把原图再画一遍，看起来就是亮的
            painter.drawPixmap(rect, self.original_pixmap, rect)
            
            # 画红色边框
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.is_snipping = True
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.is_snipping = False
        self.close()
        
        rect = QRect(self.begin, self.end).normalized()
        
        # 打印一下选区大小，确认是否太小
        print(f"📏 Selection size: {rect.width()} x {rect.height()}")

        if rect.width() < 10 or rect.height() < 10:
            print("⚠️ Area too small, ignored.")
            QApplication.quit()
            return

        cropped = self.original_pixmap.copy(rect)
        
        # --- 核心修改：使用绝对路径保存，并打印出来 ---
        import os
        filename = "temp_snip.png"
        abs_path = os.path.abspath(filename) # 获取绝对路径
        
        cropped.save(abs_path)
        print(f"✅ Image saved to: {abs_path}")  # <--- 看这行输出！
        
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    
    # 延迟 1 秒启动，方便你切到想截图的界面
    print("⏳ Starting in 1 seconds... Switch to your target window!")
    # 注意：在 WSL2 里，sleep 可能阻塞主线程导致 GUI 出不来
    # 我们用 QTimer 触发
    from PyQt6.QtCore import QTimer
    
    snipper = SnippingWidget()
    
    # 模拟“触发”截图（比如按了快捷键）
    # 在真实 App 里，这里会绑定全局热键
    snipper.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()