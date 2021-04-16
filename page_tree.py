from typing import Iterable
from PIL import ImageFont, ImageDraw, Image

DEBUG = True

class MoveDraw:
    # Note: as you can see only text is supported

    def __init__(self, imdraw: ImageDraw, func):
        self._imdraw = imdraw
        self._func = func
        # TODO enforce evaluation of MoveDraw(MoveDraw(...))

    def text(self, xy, *args, **kwargs):
        return self._imdraw.text(self._func(xy), *args, **kwargs)

class Node:

    def draw_on(self, draw: ImageDraw):
        pass


class YSplit:

    def __init__(self, split: float, top: Node, bottom: Node):
        self.split = split
        self.top = top
        self.bottom = bottom

    def draw_on(self, draw: ImageDraw):

        if DEBUG:
            draw.line(((0, self.split), (100, self.split)))

        self.top.draw_on(draw)

        def move(xy):
            x, y = xy
            return x, self.split + y

        self.bottom.draw_on(MoveDraw(draw, move))


class XSplit:

    def __init__(self, split: float, left: Node, right: Node):
        self.split = split
        self.left = left
        self.right = right

    def draw_on(self, draw: ImageDraw):
        if DEBUG:
            draw.line(((self.split, 0), (self.split, 100)))

        self.left.draw_on(draw)

        def move(xy):
            x, y = xy
            return self.split + x, y

        self.right.draw_on(MoveDraw(draw, move))

class Pad:

    def __init__(self, top: int, left: int, node: Node):
        self._ptop = top
        self._pleft = left
        self._node = node

    def draw_on(self, draw: ImageDraw):
        def move(xy):
            x, y = xy
            return x + self._pleft, y + self._ptop
        self._node.draw_on(MoveDraw(draw, move))


class TextLeaf(Node):

    def __init__(self, font: ImageFont.FreeTypeFont,  lines: Iterable[str]):
        self._font = font
        self._lines = lines

    def draw_on(self, draw: ImageDraw):
        letter_width, letter_height = self._font.getsize('Z')
        line_height = int(letter_height * 1.2)
        for line_no, line in enumerate(self._lines):
            draw.text(xy=(0, line_no * line_height), text=line, font=self._font, fill='black')



class FormulaLeaf(Node):
    pass

class ImageLeaf(Node):
    pass
