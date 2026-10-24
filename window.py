import os
import sys

import cv2

from face_engine import resource_path

WINDOW_TITLE = "Facial Unlock"

GREEN = (0, 200, 0)
RED = (0, 0, 220)
ORANGE = (0, 120, 180)
GRAY = (60, 60, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

ICON_ICNS = resource_path(os.path.join("assets", "icon", "icon.icns"))
ICON_ICO = resource_path(os.path.join("assets", "icon", "icon.ico"))


def set_app_icon():
    # macOS: troca o ícone do Python no Dock pelo ícone do app
    if sys.platform == "darwin":
        try:
            from AppKit import NSApplication, NSImage

            image = NSImage.alloc().initWithContentsOfFile_(ICON_ICNS)
            NSApplication.sharedApplication().setApplicationIconImage_(image)
        except Exception as e:
            print(f"Não consegui carregar o ícone: {ICON_ICNS} ({e})")

    # Windows: faz a barra de tarefas usar o ícone do app (em vez do ícone do Python)
    elif sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("facial.unlock")
        except Exception:
            pass


def set_window_icon():
    # Windows: aplica o .ico na janela do OpenCV (título + barra de tarefas)
    if sys.platform != "win32":
        return
    try:
        import ctypes

        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, WINDOW_TITLE)
        if not hwnd:
            return
        IMAGE_ICON, LR_LOADFROMFILE, LR_DEFAULTSIZE = 1, 0x10, 0x40
        WM_SETICON, ICON_SMALL, ICON_BIG = 0x80, 0, 1
        icon = user32.LoadImageW(None, ICON_ICO, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, icon)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, icon)
    except Exception as e:
        print(f"Não consegui carregar o ícone: {ICON_ICO} ({e})")


class CameraWindow:
    """Abre a webcam e a janela do app. Use com `with CameraWindow(...) as win:`."""

    def __init__(self, hint, camera_index=0):
        self.hint = hint
        self.camera_index = camera_index
        self.camera = None

    def __enter__(self):
        set_app_icon()
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            raise RuntimeError("Não foi possível abrir a webcam.")
        cv2.namedWindow(WINDOW_TITLE)
        set_window_icon()
        return self

    def __exit__(self, *exc):
        self.camera.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # no macOS a janela só fecha de verdade depois de processar os eventos

    def read(self):
        ok, frame = self.camera.read()
        # espelha, como um espelho de verdade
        return cv2.flip(frame, 1) if ok else None

    def show(self, frame, wait_ms=1):
        """Mostra o frame e retorna a tecla apertada (em minúscula)."""
        self.draw_hint(frame)
        cv2.imshow(WINDOW_TITLE, frame)
        key = cv2.waitKey(wait_ms) & 0xFF
        return chr(key).lower() if key != 255 else ""

    # ---------- desenhos ----------

    def draw_hint(self, frame):
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (0, h - 40), (w, h), BLACK, -1)
        cv2.putText(frame, self.hint, (15, h - 13), cv2.FONT_HERSHEY_SIMPLEX, 0.65, WHITE, 1)

    @staticmethod
    def draw_bar(frame, text, color):
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), color, -1)
        cv2.putText(frame, text, (15, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)

    @staticmethod
    def draw_text(frame, text, y):
        cv2.putText(frame, text, (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)

    @staticmethod
    def draw_face(frame, face, color, label=None):
        x, y, w, h = face[:4].astype(int)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        if label:
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    @staticmethod
    def draw_progress(frame, done, total):
        w = frame.shape[1]
        cv2.rectangle(frame, (15, 60), (w - 15, 80), WHITE, 2)
        cv2.rectangle(frame, (15, 60), (15 + int((w - 30) * done / total), 80), GREEN, -1)
