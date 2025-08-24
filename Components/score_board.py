import cv2

class ScoreBoard:
    piece_values = {
        "P": 1, "K": 3, "B": 3, "R": 5, "Q": 9
        ,"pawn": 1, "knight": 3, "bishop": 3, "rook": 5, "queen": 9
    }

    def __init__(self, player_color: str):
        self.score = 0
        self.player_color = player_color

    def on_capture(self, data):
        captured_piece = data["piece"]
        if data["by"] == self.player_color:
            self.score += self.piece_values.get(captured_piece.id[0], 0)

    def draw_on(self, img, x: int, y: int):
        text = f"{self.player_color} score: {self.score}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 2
        color = (255, 255, 0) if self.player_color == "white" else (0, 255, 255)

        # חישוב גודל הטקסט לקופסת רקע
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
        margin = 10
        top_left = (x - margin, y - text_h - margin)
        bottom_right = (x + text_w + margin, y + margin)

        # ציור רקע כהה חצי שקוף
        cv2.rectangle(img, top_left, bottom_right, (30, 30, 30), -1)

        # ציור הטקסט
        cv2.putText(img, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
