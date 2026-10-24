import sys

from face_engine import FACE_DATA, FaceEngine
from window import GRAY, GREEN, ORANGE, RED, WHITE, CameraWindow

# quantas amostras do rosto gravar
SAMPLES = 20
# grava 1 amostra a cada N frames, para pegar ângulos um pouco diferentes
EVERY = 4


def register(engine=None, reset=False):
    """Grava o rosto do dono. Retorna True se salvou."""
    engine = engine or FaceEngine()
    saved = 0 if reset else len(engine.known_faces)
    samples = []
    recording = False
    frame_count = 0

    with CameraWindow("ESPACO: comecar a gravar   Q: sair") as win:
        while True:
            frame = win.read()
            if frame is None:
                return False
            faces = engine.detect(frame)

            if not recording:
                if saved:
                    win.draw_text(frame, f"{saved} amostras salvas - esta gravacao vai somar a elas", 110)
                if len(faces) == 1:
                    win.draw_bar(frame, "Rosto encontrado - aperte ESPACO", GRAY)
                    win.draw_face(frame, faces[0], WHITE)
                else:
                    win.draw_bar(frame, "Fique sozinho na frente da camera", RED)
            else:
                win.draw_bar(frame, f"Gravando rosto... {len(samples)}/{SAMPLES}", ORANGE)
                win.draw_progress(frame, len(samples), SAMPLES)
                win.draw_text(frame, "Mexa a cabeca devagar", 110)
                frame_count += 1
                if len(faces) == 1:
                    win.draw_face(frame, faces[0], GREEN)
                    if frame_count % EVERY == 0:
                        samples.append(engine.feature(frame, faces[0]))

            if len(samples) >= SAMPLES:
                engine.save(samples, reset=reset)
                win.draw_bar(frame, "Rosto salvo!", GREEN)
                win.show(frame, wait_ms=1500)
                print(f"Rosto salvo em {FACE_DATA} ({len(engine.known_faces)} amostras no total)")
                return True

            key = win.show(frame)
            if key == "q":
                print("Cadastro cancelado.")
                return False
            if key == " " and len(faces) == 1:
                recording = True


if __name__ == "__main__":
    # --novo apaga as amostras antigas e começa o cadastro do zero
    register(reset="--novo" in sys.argv)
