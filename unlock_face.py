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

# modo sem janela (tela de bloqueio): tempo máximo com a câmera ligada
CHECK_SECONDS = 20
# códigos de saída do modo sem janela, lidos pelo plugin da tela de bloqueio
EXIT_UNLOCKED, EXIT_DENIED, EXIT_NO_FACE, EXIT_CAMERA_ERROR = 0, 1, 2, 3

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


def unlock(engine=None, headless=False, timeout=None):
    """Reconhece o dono e pede para ficar parado e sorrir (prova de que não é uma foto).

    - headless: sem janela; escreve "STATUS <etapa>" no terminal para o plugin da tela de bloqueio
    - timeout: segundos até desistir (None = sem limite)

    Retorna True quando passa em todas as etapas.
    """
    engine = engine or FaceEngine()
    # no modo sem janela, as mensagens para pessoas vão para o stderr e o stdout fica só com STATUS
    log = (lambda *a: print(*a, file=sys.stderr)) if headless else print
    if not engine.has_owner():
        log("No face registered.")
        return False
    liveness = Liveness()
    give_up = time.time() + timeout if timeout else None
    last_status = None

    def status(name):
        # avisa a etapa atual (só quando muda): looking, unknown, still, smile, unlocked, timeout
        nonlocal last_status
        if headless and name != last_status:
            print(f"STATUS {name}", flush=True)
            last_status = name

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
            log(f"  {LABELS[step]}: OK")
        step, count = new_step, 0
        deadline = time.time() + STEP_SECONDS
        status("still" if new_step == NEUTRAL else "smile")

    with CameraWindow("Q: quit", headless=headless) as win:
        while True:
            if give_up and time.time() > give_up:
                log("Time is up.")
                status("timeout")
                return False
            frame = win.read()
            if frame is None:
                return False
            faces = engine.detect(frame)

            # ---------- etapa 1: reconhecer o rosto ----------
            if step == RECOGNIZE:
                if len(faces) == 0:
                    recent.append(False)
                    status("looking")
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
                        status("unknown")
                        win.draw_bar(frame, "Unknown face", RED)
                        win.draw_face(frame, face, RED, f"Unknown ({score:.2f})")

                if sum(recent) >= MATCH_FRAMES:
                    log("Face recognized. Challenge: still -> smile")
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
                    log(f"  {LABELS[step]}: time is up "
                          f"(best smile: {best_smile - 1:+.0%} of {SMILE_GAIN - 1:+.0%}). Restarting...")
                    step = RECOGNIZE
                    recent.clear()
                    status("looking")
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
                            log(f"  {LABELS[SMILE]}: OK")
                            log("Unlocked!")
                            status("unlocked")
                            win.draw_bar(frame, "Unlocked!", GREEN)
                            win.show(frame, wait_ms=800)
                            return True
                else:
                    # sumiu o rosto ou apareceu outro: zera a contagem
                    count = 0

            if win.show(frame) == "q":
                log("Test cancelled.")
                return False


def check(timeout=CHECK_SECONDS):
    """Modo sem janela para a tela de bloqueio. Retorna o código de saída do programa.

    0 = é o dono, 1 = não é / tempo esgotado, 2 = nenhum rosto cadastrado, 3 = erro na câmera
    """
    engine = FaceEngine()
    if not engine.has_owner():
        print("RESULT no_face", flush=True)
        return EXIT_NO_FACE
    try:
        unlocked = unlock(engine, headless=True, timeout=timeout)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        print("RESULT camera_error", flush=True)
        return EXIT_CAMERA_ERROR
    print(f"RESULT {'unlocked' if unlocked else 'denied'}", flush=True)
    return EXIT_UNLOCKED if unlocked else EXIT_DENIED
