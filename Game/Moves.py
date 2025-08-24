import pathlib
from typing import List, Dict, Tuple, Optional

class Moves:
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        self.rel_moves = self._load_moves(txt_path)
        self.W, self.H = dims
        print(f"[LOAD] Moves from: {txt_path}")

    def _load_moves(self, txt_path):
        moves = []
        with open(txt_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split(",")
                row = int(parts[0])
                col = int(parts[1].split(":")[0])  
                moves.append((row, col))
        return moves

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        moves = []
        for dr, dc in self.rel_moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.H and 0 <= nc < self.W:
                moves.append((nr, nc))
        return moves


