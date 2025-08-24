from Game.Board import Board
from Game.Physics import Physics


class PhysicsFactory:      
    def __init__(self, board: Board): self.board = board
    def create(self, start_cell, cfg,publisher) -> Physics:
        return Physics(start_cell, self.board, cfg.get("speed_m_per_sec", 1.0),publisher)
