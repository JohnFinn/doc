from torch.utils.data import Dataset
from PIL import Image, ImageFont, ImageDraw
import random
import string
from page_tree import *

class RandomTextDataset(Dataset):

    def __init__(self, length: int, font = ImageFont.truetype('/usr/share/fonts/TTF/Vera.ttf', 8)):
        self._length = length
        self._font = font
        super().__init__()

    def __len__(self):
        return self._length

    def __getitem__(self, idx: int):
        letter_width, letter_height = self._font.getsize('Z')
        line_len = 40
        line_cnt = 10
        line_height = int(letter_height * 1.2)


        tree = PageTreeXSplit(
            250,
            PageTreePad(50, 50, PageTreeTextLeaf(self._font, (random_string(line_len) for _ in range(line_cnt))) ),
            PageTreePad(50, 50, PageTreeTextLeaf(self._font, (random_string(line_len) for _ in range(line_cnt))) )
        )
        img = Image.new('L', (700, 500), 'white')
        draw = ImageDraw.Draw(img)
        tree.draw_on(draw)

        return img

def random_string(length: int):
    return ''.join((random.choice(string.ascii_letters + ' ' * 10) for _ in range(length)))
