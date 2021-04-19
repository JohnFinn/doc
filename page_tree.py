import textwrap
import math
from typing import Iterable, Tuple
from PIL import ImageFont, ImageDraw, Image

BoxT = Tuple[int, int, int, int]

class Node:

    def draw_on(self, image: Image, box: BoxT, debug=False):
        pass

    def draw_debug_info(self, image: Image, box: BoxT):
        pass

    def leafs(self, box: BoxT) -> Iterable[Tuple['Node', BoxT]]:
        pass

class YSplit:

    def __init__(self, split: float, top: Node, bottom: Node):
        self.split = split
        self.top = top
        self.bottom = bottom

    def draw_on(self, image: Image, box: BoxT, debug=False):
        draw = ImageDraw.Draw(image)
        top_box, bottom_box = self.ysplit(box)
        self.top.draw_on(draw, top_box, debug)
        self.bottom.draw_on(draw, bottom_box, debug)
        if debug:
            self.draw_debug_info(draw, box)

    def draw_debug_info(self, image: Image, box: BoxT):
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = box
        abs_split = y1 + self.split * (y2 - y1)
        draw.line(((x1, abs_split), (x2, abs_split)))

    def ysplit(self, box: BoxT) -> (BoxT, BoxT):
        x1, y1, x2, y2 = box
        abs_split = y1 + self.split * (y2 - y1)
        return (x1, y1, x2, abs_split), (x1, abs_split, x2, y2)

    def leafs(self, box: BoxT) -> Iterable[Tuple[Node, BoxT]]:
        top, bottom = self.ysplit(box)
        yield from self.top.leafs(top)
        yield from self.bottom.leafs(bottom)


class XSplit:

    def __init__(self, split: float, left: Node, right: Node):
        self.split = split
        self.left = left
        self.right = right

    def draw_on(self, image: Image, box: BoxT, debug=False):
        draw = ImageDraw.Draw(image)
        left_box, right_box = self.xsplit(box)
        self.left.draw_on(draw, left_box, debug)
        self.right.draw_on(draw, right_box, debug)
        if debug:
            self.draw_debug_info(draw, box)

    def draw_debug_info(self, image: Image, box: BoxT):
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = box
        abs_split = x1 + self.split * (x2 - x1)
        draw.line(((abs_split, y1), (abs_split, y2)))

    def xsplit(self, box: BoxT) -> (BoxT, BoxT):
        x1, y1, x2, y2 = box
        abs_split = x1 + self.split * (x2 - x1)
        return (x1, y1, abs_split, y2), (abs_split, y1, x2, y2)

    def leafs(self, box: BoxT) -> Iterable[Tuple[Node, BoxT]]:
        left, right = self.xsplit(box)
        yield from self.left.leafs(left)
        yield from self.right.leafs(right)


class Pad:

    def __init__(self, top: float, left: float, bottom: float, right: float, node: Node):
        self.ptop = top
        self.pleft = left
        self.pbottom = bottom
        self.pright = right
        self.node = node

    def draw_on(self, image: Image, box: BoxT, debug=False):
        draw = ImageDraw.Draw(image)
        padded_box = self.pad(box)
        self.node.draw_on(draw, padded_box, debug)
        if debug:
            self.draw_debug_info(draw, box)

    def draw_debug_info(self, image: Image, box: BoxT):
        draw = ImageDraw.Draw(image)
        padded_box = self.pad(box)
        draw.rectangle(padded_box)

    def pad(self, box: BoxT) -> BoxT:
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        ptop = self.ptop * h
        pbottom = self.pbottom * h
        pleft = self.pleft * w
        pright = self.pright * w
        return (x1 + pleft, y1 + ptop, x2 - pright, y2 - pbottom)

    def leafs(self, box: BoxT) -> Iterable[Tuple[Node, BoxT]]:
        yield from self.node.leafs(self.pad(box))


class Rotate(Node):

    def __init__(self, angle: float, node: Node):
        self.angle = angle
        self.node = node

    def draw_on(self, image: Image, box: BoxT, debug=False):
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        img = Image.new('L', (w, h), 'white')
        draw = ImageDraw.Draw(img)
        self.node.draw_on(draw, box, debug=debug)
        img.rotate(self.angle, expand=True, fillcolor='white')

    def leafs(self, box: BoxT) -> Iterable[Tuple[Node, BoxT]]:
        # yield from self.node.leafs()
        raise NotImplementedError("rotation not implemented")


class TextLeaf(Node):

    def __init__(self, text: str, font: ImageFont.FreeTypeFont):
        self.font = font
        self.text = text

    def draw_on(self, image: Image, box: BoxT, debug=False):
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        letter_width, letter_height = self.font.getsize('Z')
        letter_height += 4
        width = int(w // letter_width)
        height = int(h // letter_height)
        wrapped_text = '\n'.join(textwrap.wrap(self.text, width=width)[:height])
        self.text_bbox = draw.multiline_textbbox((x1, y1), text=wrapped_text, font=self.font)
        draw.multiline_text((x1, y1), text=wrapped_text, font=self.font)
        if debug:
            self.draw_debug_info(draw, box)

    def draw_debug_info(self, image: Image, box: BoxT):
        draw = ImageDraw.Draw(image)
        draw.rectangle(self.text_bbox, outline='red')

    def leafs(self, box: BoxT) -> Iterable[Tuple[Node, BoxT]]:
        yield self, box


class FormulaLeaf(Node):

    def leafs(self, box: BoxT) -> Iterable[Tuple[Node, BoxT]]:
        yield self, box


class ImageLeaf(Node):

    def leafs(self, box: BoxT) -> Iterable[Tuple[Node, BoxT]]:
        yield self, box
