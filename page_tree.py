from typing import Iterable, Tuple
from PIL import ImageFont, ImageDraw, Image

DEBUG = True

class Node:

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        pass



class YSplit:

    def __init__(self, split: float, top: Node, bottom: Node):
        self.split = split
        self.top = top
        self.bottom = bottom

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        abs_split = y1 + self.split * (y2 - y1)

        if DEBUG:
            draw.line(((x1, abs_split), (x2, abs_split)))

        self.top.draw_on(draw, (x1, y1, x2, abs_split))
        self.bottom.draw_on(draw, (x1, abs_split, x2, y2))


class XSplit:

    def __init__(self, split: float, left: Node, right: Node):
        self.split = split
        self.left = left
        self.right = right

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        abs_split = x1 + self.split * (x2 - x1)
        if DEBUG:
            draw.line(((abs_split, y1), (abs_split, y2)))

        self.left.draw_on(draw, (x1, y1, abs_split, y2))
        self.right.draw_on(draw, (abs_split, y1, x2, y2))

class Pad:

    def __init__(self, top: float, left: float, bottom: float, right: float, node: Node):
        self._ptop = top
        self._pleft = left
        self._pbottom = bottom
        self._pright = right
        self._node = node

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        ptop = self._ptop * h
        pbottom = self._pbottom * h
        pleft = self._pleft * w
        pright = self._pright * w
        self._node.draw_on(draw, (x1 + pleft, y1 + ptop, x2 - pright, y2 - pbottom))


class TextLeaf(Node):

    def __init__(self, text: str, font: ImageFont.FreeTypeFont):
        self._font = font
        self._text = text

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        letter_width, letter_height = self._font.getsize('Z')
        line_height = int(letter_height * 1.2)

        line_count = h // line_height
        line_len = w // letter_width

        text_bbox = draw.multiline_textbbox((x1, y1), text=self._text, font=self._font)
        if DEBUG:
            draw.rectangle(text_bbox, outline='red')
        draw.multiline_text((x1, y1), text=self._text, font=self._font)



class FormulaLeaf(Node):
    pass

class ImageLeaf(Node):
    pass
