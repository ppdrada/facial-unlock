import math
import os

# esconde as mensagens internas do MediaPipe no terminal
os.environ.setdefault("GLOG_minloglevel", "2")

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

from face_engine import LANDMARKER_MODEL, MODELS_DIR

# pontos do MediaPipe Face Mesh
MOUTH_LEFT, MOUTH_RIGHT = 61, 291
EYE_LEFT, EYE_RIGHT = 33, 263


class Liveness:
    """Lê o rosto com o MediaPipe para provar que é uma pessoa de verdade.

    Uma foto não muda de expressão: não sorri.
    """

    def __init__(self):
        options = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=os.path.join(MODELS_DIR, LANDMARKER_MODEL)),
            num_faces=1,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

    def mouth_width(self, frame):
        """Largura da boca em relação à distância entre os olhos (aumenta ao sorrir).

        Retorna 0 se não achar rosto.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        if not result.face_landmarks:
            return 0

        h, w = frame.shape[:2]
        p = result.face_landmarks[0]
        point = lambda i: (p[i].x * w, p[i].y * h)
        dist = lambda a, b: math.dist(point(a), point(b))
        return dist(MOUTH_LEFT, MOUTH_RIGHT) / (dist(EYE_LEFT, EYE_RIGHT) or 1)
