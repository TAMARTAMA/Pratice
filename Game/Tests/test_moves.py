import pytest
import pathlib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import mock_open, patch
from Moves import Moves  # שנה את השם בהתאם לשם הקובץ שבו נמצאת מחלקת Moves

# דוגמת טקסט כאילו נלקחה מקובץ moves.txt
FAKE_FILE_CONTENT = "1,2:\n-1,0:\n0,1:\n"

@pytest.fixture
def mock_moves_file():
    """Mock לקובץ שמחזיר תוכן מהלך תקני"""
    m = mock_open(read_data=FAKE_FILE_CONTENT)
    with patch("builtins.open", m):
        yield

def test_load_moves(mock_moves_file):
    path = pathlib.Path("fake.txt")
    m = Moves(path, (8, 8))
    assert m.rel_moves == [(1, 2), (-1, 0), (0, 1)]

def test_get_moves_within_bounds(mock_moves_file):
    path = pathlib.Path("fake.txt")
    m = Moves(path, (3, 3))
    # מיקום התחלה (1,1) + מהלכים (1,2), (-1,0), (0,1)
    result = m.get_moves(1, 1)
    # רק (2,2), (0,1), (1,2) חוקיים בלוח 3x3
    assert sorted(result) == sorted([(2, 2), (0, 1), (1, 2)])

def test_get_moves_out_of_bounds(mock_moves_file):
    path = pathlib.Path("fake.txt")
    m = Moves(path, (2, 2))
    # (0,0) + מהלכים => רק (0,1) ו-(1,2) חוקיים, אבל (1,2) מחוץ לגבול
    result = m.get_moves(0, 0)
    assert result == [(0, 1)]
