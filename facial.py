import cv2


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
        self.open_camera()
        print("Webcam aberta. Pressione 'q' para sair.")
        try:
            while True:
                ok, frame = self.camera.read()
                if not ok:
                    break
                faces = self.detect_faces(frame)
                self.draw_faces(frame, faces)
                cv2.imshow("Facial Unlock", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            self.camera.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    FacialUnlock().run()
