from Game.Command import Command
from Game.Moves import Moves
from Game.Graphics import Graphics
from Game.Physics import Physics
from typing import Dict
import time


class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        self.moves, self.graphics, self.physics = moves, graphics, physics
        self.transitions: Dict[str, "State"] = {}
        self.cooldown_end_ms = 0
        self.name = None

    def __repr__(self):
        return f"State({self.name})"

    def set_transition(self, event: str, target: "State"):
        self.transitions[event] = target

    def reset(self, cmd: Command):
        self.graphics.reset(cmd)
        self.physics.reset(cmd)



    def can_transition(self, now_ms: int) -> bool:        
        return now_ms >= self.cooldown_end_ms

    def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
        nxt = self.transitions.get(cmd.type)

        if cmd.type == "Arrived" and nxt:
            print(f"[TRANSITION] Arrived: {self} → {nxt}")

            if self.name == "move":
                rest_ms = 6000  
            elif self.name == "jump":
                rest_ms = 3000  
            else:  
                rest_ms = 0

            nxt.graphics.reset(cmd)

            if rest_ms:
                p = nxt.physics
                p.start_ms = now_ms  
                p.duration_ms = rest_ms
                p.wait_only = True

                nxt.cooldown_end_ms = now_ms + rest_ms
            else:
                nxt.cooldown_end_ms = 0

            return nxt

        if nxt is None:
            print(f"[TRANSITION MISSING] {cmd.type} from state {self}")
            return self                      

        print(f"[TRANSITION] {cmd.type}: {self} → {nxt}")

        if self.can_transition(now_ms):
            nxt.reset(cmd)                   
            return nxt

        self.reset(cmd)
        return self


    def update(self, now_ms: int) -> "State":
        internal = self.physics.update(now_ms)
        if internal:
            print("[DBG] internal:", internal.type)
            return self.get_state_after_command(internal, now_ms)
        self.graphics.update(now_ms)
        return self

    def get_command(self) -> Command:
        return Command(self.physics.start_ms, "?", "Idle", [])
