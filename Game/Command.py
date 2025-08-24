from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import json
from dataclasses import dataclass, asdict
@dataclass
class Command:
    timestamp: int          # ms since game start
    piece_id: str
    type: str               # "Move" | "Jump" | …
    params: List            # payload (e.g. ["e2", "e4"])
    def to_json(self) -> str:
        return json.dumps(asdict(self))