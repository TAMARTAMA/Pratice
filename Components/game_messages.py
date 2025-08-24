import time
import cv2
class GameMessages:
    def __init__(self):
        self.messages: list[tuple[str, float]] = []  # (text, expiration_time)

    def post(self, text: str, duration_sec: float = 2.5):
        expire_time = time.time() + duration_sec
        self.messages.append((text, expire_time))

    def on_game_start(self, _=None):
        self.post("LET THE BATTLE BEGIN!", 3)

    def on_game_end(self, messenge:str):
        self.post(messenge, 5)


    def draw_on(self, img, x=400, y=50):
        now = time.time()
        self.messages = [(msg, exp) for msg, exp in self.messages if exp > now]

        for i, (msg, _) in enumerate(self.messages):
            y_offset = y + i * 40
            cv2.putText(
                img,
                msg,
                org=(x, y_offset),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,  # ← זה מה שהיה חסר
                fontScale=1.3,
                color=(0, 0, 255),
                thickness=2
            )

