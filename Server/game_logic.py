# game_logic.py

from typing import Tuple, Dict

class GameLogic:
    def __init__(self):
        self.board = self._create_initial_board()

    def _create_initial_board(self):
        return {"Q_white": (0, 3), "Q_black": (7, 3)}  # רק דוגמה

    def is_move_legal(self, player_id: str, piece: str, to_pos: Tuple[int, int]) -> bool:
        # כאן בדיקה אם מותר להזיז (פשוט מאוד לדוגמה)
        if piece not in self.board:
            return False
        # בודק שהמלכה זזה באלכסון/ישר - דוגמה בלבד
        from_pos = self.board[piece]
        return from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1] or abs(from_pos[0] - to_pos[0]) == abs(from_pos[1] - to_pos[1])

    def move_piece(self, piece: str, to_pos: Tuple[int, int]):
        self.board[piece] = to_pos

    def get_board_state(self) -> Dict[str, Tuple[int, int]]:
        return self.board
