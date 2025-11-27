import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread, pyqtSignal

from snip_overlay import SnipOverlay
from ocr_engine import OcrHandler

# 为了不卡死界面，OCR 必须在后台线程跑
class OcrThread(QThread):
    finished = pyqtSignal(str, list) # latex, texts

    def __init__(self, handler, img):
        super().__init__()
        self.handler = handler
        self.img = img

    def run(self):
        latex, texts = self.handler.run(self.img)
        self.finished.emit(latex, texts)

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 1. 初始化 OCR 引擎 (稍微耗时)
        self.ocr_handler = OcrHandler()
        
        # 2. 初始化截图窗口
        self.snipper = SnipOverlay()
        self.snipper.snip_captured.connect(self.on_snip_captured)
        
        # 3. 初始化托盘
        self.setup_tray()

    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        # 这里用标准图标，实际发布时换成你的 logo
        self.tray.setIcon(QIcon.fromTheme("edit-copy")) 
        
        menu = QMenu()
        
        # 截图按钮
        action_snip = QAction("截图 (Snip)", parent=menu)
        action_snip.triggered.connect(self.start_snip)
        menu.addAction(action_snip)
        
        # 退出按钮
        action_quit = QAction("退出 (Quit)", parent=menu)
        action_quit.triggered.connect(self.app.quit)
        menu.addAction(action_quit)
        
        self.tray.setContextMenu(menu)
        self.tray.setVisible(True)
        
        print("✅ App is running in tray.")

    def start_snip(self):
        print("📸 Snipping started...")
        self.snipper.start_snip()

    def on_snip_captured(self, img):
        print("🔄 Processing image...")
        # 启动线程跑 OCR
        self.thread = OcrThread(self.ocr_handler, img)
        self.thread.finished.connect(self.show_result)
        self.thread.start()

    def show_result(self, latex, texts):
        print("-" * 30)
        print(f"LaTeX: {latex}")
        print(f"Text: {texts}")
        print("-" * 30)
        
        # 这里把结果复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(latex)
        
        # 弹个窗提示 (后面可以改成漂亮的 ResultWindow)
        msg = QMessageBox()
        msg.setWindowTitle("Result Copied!")
        msg.setText(f"LaTeX copied to clipboard.\n\nRaw Text:\n{texts}")
        msg.exec()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = MainApp()
    app.run()