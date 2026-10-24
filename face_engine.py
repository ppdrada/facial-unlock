import os
import sys
import urllib.request

import cv2
import numpy as np

# similaridade mínima (cosseno) para considerar o mesmo rosto — valor recomendado pelo SFace
MATCH_THRESHOLD = 0.363

MODELS_URL = "https://github.com/opencv/opencv_zoo/raw/main/models"
DETECTOR_MODEL = "face_detection_yunet_2023mar.onnx"
RECOGNIZER_MODEL = "face_recognition_sface_2021dec.onnx"
MODELS = {
    DETECTOR_MODEL: f"{MODELS_URL}/face_detection_yunet/{DETECTOR_MODEL}",
    RECOGNIZER_MODEL: f"{MODELS_URL}/face_recognition_sface/{RECOGNIZER_MODEL}",
}


def resource_path(rel):
    # funciona tanto rodando o .py quanto o executável gerado pelo PyInstaller
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


MODELS_DIR = resource_path("models")
DATA_DIR = resource_path("data")
FACE_DATA = os.path.join(DATA_DIR, "face.npy")


def ensure_models():
    # baixa os modelos do OpenCV Zoo na primeira execução
    os.makedirs(MODELS_DIR, exist_ok=True)
    for name, url in MODELS.items():
        path = os.path.join(MODELS_DIR, name)
        if not os.path.exists(path):
            print(f"Baixando {name}...")
            urllib.request.urlretrieve(url, path)


class FaceEngine:
    """Detecta rostos, extrai as características e compara com o rosto salvo."""

    def __init__(self):
        ensure_models()
        self.detector = cv2.FaceDetectorYN.create(
            os.path.join(MODELS_DIR, DETECTOR_MODEL), "", (320, 320), 0.9
        )
        self.recognizer = cv2.FaceRecognizerSF.create(
            os.path.join(MODELS_DIR, RECOGNIZER_MODEL), ""
        )
        self.known_faces = self.load()

    def detect(self, frame):
        h, w = frame.shape[:2]
        self.detector.setInputSize((w, h))
        _, faces = self.detector.detect(frame)
        return faces if faces is not None else []

    def feature(self, frame, face):
        aligned = self.recognizer.alignCrop(frame, face)
        return self.recognizer.feature(aligned)[0]

    def score(self, feature):
        # maior similaridade entre o rosto atual e as amostras salvas
        return max(
            self.recognizer.match(feature[None], known[None], cv2.FaceRecognizerSF_FR_COSINE)
            for known in self.known_faces
        )

    def has_owner(self):
        return len(self.known_faces) > 0

    def load(self):
        if os.path.exists(FACE_DATA):
            return list(np.load(FACE_DATA))
        return []

    def save(self, samples, reset=False):
        # por padrão soma às amostras já salvas (ex.: com fone, de óculos, outra luz)
        self.known_faces = list(samples) if reset else self.known_faces + list(samples)
        os.makedirs(DATA_DIR, exist_ok=True)
        np.save(FACE_DATA, np.array(self.known_faces))
