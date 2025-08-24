# test_physics.py
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import Mock
from Physics import Physics
from Command import Command  # ודא שהמחלקה קיימת וכוללת לפחות .timestamp, .type, .params

class DummyBoard:
    def __init__(self):
        self.cell_W_pix = 64
        self.cell_H_pix = 64
        self.offset_x = 0
        self.offset_y = 0
def test_reset_move_publishes_correct_topics():
    publisher = Mock()
    board = DummyBoard()
    physics = Physics((2, 2), board, publisher=publisher)

    cmd = Command(timestamp=1000, type="move", piece_id="", params=[(3, 2)])
    physics.reset(cmd)

    assert physics.end_cell == (3, 2)
    assert physics.start_ms == 1000
    assert physics.wait_only is False
    assert physics.duration_ms > 0

    publisher.publish.assert_any_call("piece_moved_sound", "move")
    publisher.publish.assert_any_call("piece_moved", cmd)
def test_update_progresses_and_arrives():
    publisher = Mock()
    board = DummyBoard()
    physics = Physics((0, 0), board, publisher=publisher)
    cmd = Command(timestamp=0, type="move", piece_id="", params=[(1, 1)])
    physics.reset(cmd)

    result = physics.update(now_ms=10)  # עדיין לא הגיע
    assert result is None
    assert isinstance(physics.curr_px, tuple)

    result = physics.update(now_ms=5000)  # אמור כבר להגיע
    assert isinstance(result, Command)
    assert result.piece_id == "?"
def test_captured_and_in_captured():
    publisher = Mock()
    board = DummyBoard()
    physics = Physics((0, 0), board, publisher=publisher)

    physics.captured()
    assert physics.can_be_captured() is True
    publisher.publish.assert_called_with("piece_captured_sound", "piece_captured")

    dummy_cmd = Command(timestamp=1234, type="move", piece_id="Move", params=[])
    physics.in_captured("piece_captured_B", {"dummy": True}, dummy_cmd)

    publisher.publish.assert_any_call("piece_captured_B", {"dummy": True})
    publisher.publish.assert_any_call("piece_captured_history_B", dummy_cmd)
def test_get_pos_before_and_after_update():
    publisher = Mock()
    board = DummyBoard()
    physics = Physics((1, 1), board, publisher=publisher)

    pos_before = physics.get_pos()
    assert pos_before == (64, 64)

    cmd = Command(timestamp=0, type="move", piece_id="", params=[(2, 2)])
    physics.reset(cmd)
    physics.update(now_ms=1000)

    pos_after = physics.get_pos()
    assert isinstance(pos_after, tuple)
    assert pos_after != pos_before
