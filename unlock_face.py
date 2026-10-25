import statistics
import subprocess
import sys
import time
from collections import deque

from face_engine import MATCH_THRESHOLD, FaceEngine
from liveness import Liveness
from window import GRAY, GREEN, ORANGE, RED, WHITE, CameraWindow

# reconhece quando o rosto bate em MATCH_FRAMES dos últimos RECENT_FRAMES frames
MATCH_FRAMES = 5
RECENT_FRAMES = 10

# desafio anti-foto, em ordem: parado -> sorriso
STEP_SECONDS = 3        # tempo de cada passo
SMILE_GAIN = 1.10       # o sorriso precisa deixar a boca 10% mais larga que parada
SMILE_FRAMES = 3        # frames seguidos sorrindo
# sorrindo o rosto fica menos parecido, então aceita uma nota um pouco menor
CHALLENGE_MATCH_THRESHOLD = 0.3

RECOGNIZE, NEUTRAL, SMILE = "reconhecer", "parado", "sorriso"
STEPS = [NEUTRAL, SMILE]
INSTRUCTIONS = {NEUTRAL: "Stay still", SMILE: "Now smile!"}
LABELS = {NEUTRAL: "Still", SMILE: "Smile"}


def open_calculator():
    # teste de desbloqueio: abre a calculadora do sistema
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Calculator"])
    elif sys.platform == "win32":
        subprocess.Popen("calc.exe")


def draw_checklist(win, frame, step):
    # lista dos passos: OK nos concluídos, ">" no atual
    current = STEPS.index(step)
    for i, s in enumerate(STEPS):
        mark = "[OK]" if i < current else (" >  " if i == current else "[  ]")
        color = GREEN if i < current else (ORANGE if i == current else WHITE)
        win.draw_text(frame, f"{mark} {LABELS[s]}", 150 + i * 35, color)


def unlock(engine=None):
    """Reconhece o dono e pede para ficar parado e sorrir (prova de que não é uma foto).

    Retorna True quando passa em todas as etapas.
    """
    engine = engine or FaceEngine()
    if not engine.has_owner():
        print("No face registered.")
        return False
    liveness = Liveness()

    step = RECOGNIZE
    recent = deque(maxlen=RECENT_FRAMES)
    neutral_mouth = []  # largura da boca parada, para comparar com o sorriso
    baseline = 1
    count = 0
    best_smile = 1
    deadline = 0

    def next_step(new_step):
        nonlocal step, count, deadline
        if step in STEPS:
            print(f"  {LABELS[step]}: OK")
        step, count = new_step, 0
        deadline = time.time() + STEP_SECONDS

    with CameraWindow("Q: quit") as win:
        while True:
            frame = win.read()
            if frame is None:
                return False
            faces = engine.detect(frame)

            # ---------- etapa 1: reconhecer o rosto ----------
            if step == RECOGNIZE:
                if len(faces) == 0:
                    recent.append(False)
                    win.draw_bar(frame, "Looking for a face...", GRAY)
                else:
                    face = faces[0]
                    score = engine.score(engine.feature(frame, face))
                    if score >= MATCH_THRESHOLD:
                        recent.append(True)
                        win.draw_bar(frame, "Face recognized!", GREEN)
                        win.draw_face(frame, face, GREEN, f"You ({score:.2f})")
                    else:
                        recent.append(False)
                        win.draw_bar(frame, "Unknown face", RED)
                        win.draw_face(frame, face, RED, f"Unknown ({score:.2f})")

                if sum(recent) >= MATCH_FRAMES:
                    print("Face recognized. Challenge: still -> smile")
                    neutral_mouth = []
                    best_smile = 1
                    next_step(NEUTRAL)

            # ---------- etapas 2 e 3: parado -> sorriso ----------
            else:
                remaining = max(0, int(deadline - time.time()) + 1)
                win.draw_bar(frame, f"Step {STEPS.index(step) + 1} of {len(STEPS)}  ({remaining}s)", ORANGE)
                draw_checklist(win, frame, step)
                # o que fazer: legenda grande embaixo do rosto
                win.draw_caption(frame, INSTRUCTIONS[step], faces[0] if len(faces) == 1 else None, WHITE)

                if step == NEUTRAL and time.time() > deadline and neutral_mouth:
                    # terminou os segundos parado: a boca "normal" vira a referência do sorriso
                    baseline = statistics.median(neutral_mouth)
                    next_step(SMILE)
                elif time.time() > deadline:
                    # não cumpriu a tempo: volta para o começo
                    print(f"  {LABELS[step]}: time is up "
                          f"(best smile: {best_smile - 1:+.0%} of {SMILE_GAIN - 1:+.0%}). Restarting...")
                    step = RECOGNIZE
                    recent.clear()
                elif len(faces) == 1:
                    face = faces[0]
                    is_owner = engine.score(engine.feature(frame, face)) >= CHALLENGE_MATCH_THRESHOLD
                    mouth = liveness.mouth_width(frame)
                    win.draw_face(frame, face, GREEN if is_owner else RED)

                    if step == NEUTRAL:
                        if is_owner and mouth:
                            neutral_mouth.append(mouth)
                    else:
                        gain = mouth / baseline
                        best_smile = max(best_smile, gain)
                        win.draw_text(frame, f"smile: {gain - 1:+.0%}  (need {SMILE_GAIN - 1:+.0%})", 110)
                        count = count + 1 if (is_owner and gain >= SMILE_GAIN) else 0
                        if count >= SMILE_FRAMES:
                            print(f"  {LABELS[SMILE]}: OK")
                            print("Unlocked!")
                            win.draw_bar(frame, "Unlocked!", GREEN)
                            win.show(frame, wait_ms=800)
                            return True
                else:
                    # sumiu o rosto ou apareceu outro: zera a contagem
                    count = 0

            if win.show(frame) == "q":
                print("Test cancelled.")
                return False
