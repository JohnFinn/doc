from torch.utils.data import Dataset
from PIL import Image, ImageFont, ImageDraw
import random
import string

class RandomTextDataset(Dataset):

    def __init__(self, length: int, font = ImageFont.truetype('/usr/share/fonts/TTF/Vera.ttf', 16)):
        self._length = length
        self._font = font
        super().__init__()

    def __len__(self):
        return self._length

    def __getitem__(self, idx: int):
        letter_width, letter_height = self._font.getsize('Z')
        right_padding = 50
        left_padding = 50
        top_padding = 50
        bottom_padding = 50
        line_len = 80
        line_cnt = 10
        line_height = int(letter_height * 1.2)
        img = Image.new('L', (left_padding + right_padding + letter_width * line_len, top_padding + bottom_padding + line_height * line_cnt), 'white')
        draw = ImageDraw.Draw(img)

        for line_no in range(line_cnt):
            draw.text(xy=(left_padding, top_padding + line_no * line_height), text=random_string(line_len), font=self._font, fill='black')
        return img

def random_string(length: int):
    return ''.join((random.choice(string.ascii_letters + ' ' * 10) for _ in range(length)))
