import os
import sys

import cv2

WINDOW_TITLE = "Facial Unlock"


def resource_path(rel):
    # funciona tanto rodando o .py quanto o executável gerado pelo PyInstaller
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


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


class FacialUnlock:
    """Abre a webcam e detecta rostos em tempo real."""

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None
        self.detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def open_camera(self):
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            raise RuntimeError("Não foi possível abrir a webcam.")

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    def draw_faces(self, frame, faces):
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    def run(self):
        set_app_icon()
        self.open_camera()
        print("Webcam aberta. Pressione 'q' para sair.")
        cv2.namedWindow(WINDOW_TITLE)
        set_window_icon()
        try:
            while True:
                ok, frame = self.camera.read()
                if not ok:
                    break
                faces = self.detect_faces(frame)
                self.draw_faces(frame, faces)
                cv2.imshow(WINDOW_TITLE, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            self.camera.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    FacialUnlock().run()
