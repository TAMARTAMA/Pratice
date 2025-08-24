import pathlib
from typing import Dict, Tuple
import json
from Game.Board import Board
from Game.GraphicsFactory import GraphicsFactory
from Game.Moves import Moves
from Game.PhysicsFactory import PhysicsFactory
from Game.Piece import Piece
from Game.State import State


class PieceFactory:
    def __init__(self, board: Board,publisher):
        self.board = board
        self.physics_factory = PhysicsFactory(board)
        self.graphics_factory = GraphicsFactory()
        self.templates: Dict[str, State] = {}
        self.publisher = publisher

    def generate_library(self, pieces_root: pathlib.Path):
        for sub in pieces_root.iterdir():
            
            self.templates[sub.name] = self._build_state_machine(sub)

    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        board_size = (self.board.W_cells, self.board.H_cells)
        cell_px = (self.board.cell_W_pix, self.board.cell_H_pix)

        states: Dict[str, State] = {}


        for state_dir in (piece_dir / "states").iterdir():
            if not state_dir.is_dir():  
                continue

            name = state_dir.name  

            cfg_path = state_dir / "config.json"

            if cfg_path.exists() and cfg_path.read_text().strip():
                cfg = json.loads(cfg_path.read_text())
            else:
                cfg = {}

            moves = Moves(piece_dir / "moves.txt", board_size)


            graphics = self.graphics_factory.load(state_dir / "sprites",
                                                  cfg["graphics"], cell_px)
            physics = self.physics_factory.create((0, 0), cfg["physics"],self.publisher)

            state = State(moves, graphics, physics)
            state.name = name
            states[name] = state

        for name, st in states.items():
            cfg_path = piece_dir / "states" / name / "config.json"
            cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}

            nxt_name = cfg.get("physics", {}).get("next_state_when_finished")
            if nxt_name and nxt_name in states:
                st.set_transition("Arrived", states[nxt_name])

        for st in states.values():
            if "move" in states:
                st.set_transition("move", states["move"])
            if "jump" in states:
                st.set_transition("jump", states["jump"])

        return states.get("idle") or next(iter(states.values()))

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        template_idle = self.templates[p_type]

        shared_phys = self.physics_factory.create(cell, {},self.publisher)

        clone_map: Dict[State, State] = {}
        stack = [template_idle]
        while stack:
            orig = stack.pop()
            if orig in clone_map:
                continue

            clone_map[orig] = State(
                moves=orig.moves,  
                graphics=orig.graphics.copy(), 
                physics=shared_phys 
            )
            clone_map[orig].name = orig.name
            stack.extend(orig.transitions.values())

        for orig, clone in clone_map.items():
            for ev, target in orig.transitions.items():
                clone.set_transition(ev, clone_map[target])

        return Piece(f"{p_type}_{cell}", clone_map[template_idle])


