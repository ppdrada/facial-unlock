import subprocess
import sys
from collections import deque

from face_engine import MATCH_THRESHOLD, FaceEngine
from window import GRAY, GREEN, RED, CameraWindow

# desbloqueia quando o rosto bate em MATCH_FRAMES dos últimos RECENT_FRAMES frames
MATCH_FRAMES = 5
RECENT_FRAMES = 10


def open_calculator():
    # teste de desbloqueio: abre a calculadora do sistema
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Calculator"])
    elif sys.platform == "win32":
        subprocess.Popen("calc.exe")


def unlock(engine=None):
    """Olha a webcam e retorna True quando reconhece o dono."""
    engine = engine or FaceEngine()
    if not engine.has_owner():
        print("Nenhum rosto salvo.")
        return False

    recent = deque(maxlen=RECENT_FRAMES)
    with CameraWindow("Q: sair") as win:
        while True:
            frame = win.read()
            if frame is None:
                return False
            faces = engine.detect(frame)

            if len(faces) == 0:
                recent.append(False)
                win.draw_bar(frame, "Procurando rosto...", GRAY)
            else:
                face = faces[0]
                score = engine.score(engine.feature(frame, face))
                if score >= MATCH_THRESHOLD:
                    recent.append(True)
                    win.draw_bar(frame, "Rosto reconhecido!", GREEN)
                    win.draw_face(frame, face, GREEN, f"Voce ({score:.2f})")
                else:
                    recent.append(False)
                    win.draw_bar(frame, "Rosto desconhecido", RED)
                    win.draw_face(frame, face, RED, f"Desconhecido ({score:.2f})")

            if sum(recent) >= MATCH_FRAMES:
                win.show(frame, wait_ms=800)  # mostra o "reconhecido" por um instante
                return True

            if win.show(frame) == "q":
                return False
