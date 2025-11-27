from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QBuffer, QIODevice
from PyQt6.QtGui import QPainter, QPen, QColor, QGuiApplication
from PyQt6.QtWidgets import QWidget, QApplication
import io
from PIL import Image

class SnipOverlay(QWidget):
    # 定义一个信号，截图完成后发射 (image)
    snip_captured = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        # 无边框 + 置顶 + 工具窗口模式
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(0.5)
        self.is_snipping = False
        self.begin = QPoint()
        self.end = QPoint()
        self.original_pixmap = None

    def start_snip(self):
        # 截取全屏
        screen = QApplication.primaryScreen()
        self.original_pixmap = screen.grabWindow(0)
        
        # 铺满屏幕
        geom = screen.geometry()
        self.setGeometry(geom)
        self.show()
        # 变成不透明，开始自己画图
        self.setWindowOpacity(1.0)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, event):
        if not self.original_pixmap:
            return
        painter = QPainter(self)
        # 画背景图
        painter.drawPixmap(0, 0, self.original_pixmap)
        # 画半透明遮罩
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.drawRect(self.rect())

        if self.is_snipping:
            # 挖空选区 (把原图画回去)
            rect = QRect(self.begin, self.end).normalized()
            painter.drawPixmap(rect, self.original_pixmap, rect)
            # 画红框
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
        if rect.width() < 10 or rect.height() < 10:
            return

        # 1. 裁剪出选区 (QPixmap)
        cropped = self.original_pixmap.copy(rect)
        
        # 2. --- 核心修复：QPixmap -> PIL Image ---
        # 使用 QBuffer 作为中间介质，因为 QPixmap.save 不接受 Python 的 BytesIO
        qbuffer = QBuffer()
        qbuffer.open(QIODevice.OpenModeFlag.ReadWrite)
        cropped.save(qbuffer, "PNG")
        
        # 获取 bytes 数据
        # qbuffer.data() 返回 QByteArray, .data() 转为 python bytes
        image_bytes = qbuffer.data().data()
        
        # 转为 PIL Image
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        # 发送信号
        self.snip_captured.emit(pil_img)