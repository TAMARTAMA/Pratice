from typing import Callable, Dict, List, Any




# "piece_moved" — כשכלי זז

# "piece_captured" — כשיש אכילה

# "game_start" — בתחילת המשחק

# "game_end" — בסופו


class Publisher:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    def publish(self, topic: str, data: Any):
        for callback in self._subscribers.get(topic, []):
            callback(data)
