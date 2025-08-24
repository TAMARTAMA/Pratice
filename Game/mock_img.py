# mock_img.py
from img import Img

class MockImg(Img):
    """Headless Img that just records calls."""
    traj     : list[tuple[int,int]]  = []   
    txt_traj : list[tuple[tuple[int,int],str]] = []

    def __init__(self):                     
        self.img = "MOCK-PIXELS"

    def read(self, path, *_, **__):
        self.W = self.H = 1
        return self                       

    def draw_on(self, other, x, y):
        MockImg.traj.append((x, y))

    def put_text(self, txt, x, y, font_size, *_, **__):
        MockImg.txt_traj.append(((x, y), txt))

    def show(self): pass                   

    # helper for tests
    @classmethod
    def reset(cls):
        cls.traj.clear()
        cls.txt_traj.clear()
