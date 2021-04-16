import textwrap
import math
from typing import Iterable, Tuple
from PIL import ImageFont, ImageDraw, Image

class Node:

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        pass

    def draw_debug_info(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        pass


class YSplit:

    def __init__(self, split: float, top: Node, bottom: Node):
        self.split = split
        self.top = top
        self.bottom = bottom

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        top_box, bottom_box = self.ysplit(box)
        self.top.draw_on(draw, top_box)
        self.bottom.draw_on(draw, bottom_box)

    def draw_debug_info(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        abs_split = y1 + self.split * (y2 - y1)
        draw.line(((x1, abs_split), (x2, abs_split)))
        top_box, bottom_box = self.ysplit(box)
        self.top.draw_debug_info(draw, top_box)
        self.bottom.draw_debug_info(draw, bottom_box)

    def ysplit(self, box: Tuple[int, int, int, int]) -> (Tuple[int, int, int, int], Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        abs_split = y1 + self.split * (y2 - y1)
        return (x1, y1, x2, abs_split), (x1, abs_split, x2, y2)

class XSplit:

    def __init__(self, split: float, left: Node, right: Node):
        self.split = split
        self.left = left
        self.right = right

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        left_box, right_box = self.xsplit(box)
        self.left.draw_on(draw, left_box)
        self.right.draw_on(draw, right_box)

    def draw_debug_info(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        abs_split = x1 + self.split * (x2 - x1)
        draw.line(((abs_split, y1), (abs_split, y2)))
        left_box, right_box = self.xsplit(box)
        self.left.draw_debug_info(draw, left_box)
        self.right.draw_debug_info(draw, right_box)

    def xsplit(self, box: Tuple[int, int, int, int]) -> (Tuple[int, int, int, int], Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        abs_split = x1 + self.split * (x2 - x1)
        return (x1, y1, abs_split, y2), (abs_split, y1, x2, y2)


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

    def draw_debug_info(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        pass



class TextLeaf(Node):

    def __init__(self, text: str, font: ImageFont.FreeTypeFont):
        self._font = font
        self._text = text

    def draw_on(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        letter_width, letter_height = self._font.getsize('Z')
        letter_height += 4
        width = int(w // letter_width)
        height = int(h // letter_height)
        wrapped_text = '\n'.join(textwrap.wrap(self._text, width=width)[:height])
        self.text_bbox = draw.multiline_textbbox((x1, y1), text=wrapped_text, font=self._font)
        draw.multiline_text((x1, y1), text=wrapped_text, font=self._font)

    def draw_debug_info(self, draw: ImageDraw, box: Tuple[int, int, int, int]):
        draw.rectangle(self.text_bbox, outline='red')

class FormulaLeaf(Node):
    pass

class ImageLeaf(Node):
    pass
