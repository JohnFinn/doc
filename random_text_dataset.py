from torch.utils.data import Dataset
from PIL import Image, ImageFont, ImageDraw
import random
import os
import string
import textwrap
import page_tree

class RandomTextDataset(Dataset):

    def __init__(self, length: int, font = ImageFont.truetype('/usr/share/fonts/TTF/Vera.ttf', 16)):
        self._length = length
        self._font = font
        super().__init__()

    def __len__(self):
        return self._length

    def __getitem__(self, idx: int):
        letter_width, letter_height = self._font.getsize('Z')
        line_len = 30
        line_cnt = 10
        line_height = int(letter_height * 1.2)


        tree = random_page_tree(mindepth=1, maxdepth=3)
        img = Image.new('L', (1800, 1000), 'white')
        draw = ImageDraw.Draw(img)
        tree.draw_on(draw, (0, 0, img.width, img.height), debug=True)
        return img

def random_string(length: int):
    return ''.join((random.choice(string.ascii_letters + ' ' * 10) for _ in range(length)))

def random_page_tree(mindepth: int, maxdepth: int):
    if mindepth == 0:
        node = random.randint(0, 2)
    else:
        node = random.randint(1, 2)

    if node == 0 or maxdepth == 0:
        font = ImageFont.truetype(random.choice(os.listdir('/usr/share/fonts/TTF')), random.randint(8, 16))
        text = '    ' + random_string(3000)
        return page_tree.Pad(0.05, 0.05, 0.05, 0.05, page_tree.TextLeaf(font=font, text=text))
    elif node == 1:
        return page_tree.YSplit(0.2 + 0.6 * random.random(), random_page_tree(mindepth-1, maxdepth-1), random_page_tree(mindepth-1, maxdepth-1))
    elif node == 2:
        return page_tree.XSplit(0.2 + 0.6 * random.random(), random_page_tree(mindepth-1, maxdepth-1), random_page_tree(mindepth-1, maxdepth-1))
