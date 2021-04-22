import textwrap
import math
import numpy as np
from typing import Iterable, Tuple
from PIL import ImageFont, ImageDraw, Image

BoxT = Tuple[int, int, int, int]

PointT = Tuple[float, float]
BorderT = Tuple[PointT, PointT, PointT, PointT]

class Node:

    def draw_on(self, image: Image, box: BoxT, debug=False):
        pass

    def draw_debug_info(self, image: Image, box: BoxT):
        pass

    def children_border(self, border: np.ndarray) -> Iterable[Tuple['Node', np.ndarray]]:
        yield from range(0)

    def children(self) -> Iterable['Node']:
        yield from range(0)

    def __repr__(self):
        stack = []
        stack.append((self, 0))
        result = ''
        while stack:
            top, d = stack.pop()
            for c in top.children():
                stack.append((c, d + 1))
            result += ' ' * d + top.__class__.__name__ + ' ' + top.info() + '\n'
        return result

    def traverse(self, border: np.ndarray):
        stack = []
        stack.append((self, border))
        while stack:
            top, border = stack.pop()
            for c, b in top.children_border(border):
                stack.append((c, b))
            yield top, border

    def info(self):
        return ''


class YSplit(Node):

    def __init__(self, split: float, top: Node, bottom: Node):
        self.split = split
        self.top = top
        self.bottom = bottom

    def info(self):
        return f'{self.split}'

    def draw_on(self, image: Image, box: BoxT, debug=False):
        top_box, bottom_box = self.ysplit(box)
        self.top.draw_on(image, top_box, debug)
        self.bottom.draw_on(image, bottom_box, debug)
        if debug:
            self.draw_debug_info(image, box)

    def draw_debug_info(self, image: Image, box: BoxT):
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = box
        abs_split = int(y1 + self.split * (y2 - y1))
        draw.line(((x1, abs_split), (x2, abs_split)))

    def ysplit(self, box: BoxT) -> (BoxT, BoxT):
        x1, y1, x2, y2 = box
        abs_split = int(y1 + self.split * (y2 - y1))
        return (x1, y1, x2, abs_split), (x1, abs_split, x2, y2)

    def children(self):
        yield self.top
        yield self.bottom

    def children_border(self, border: np.ndarray) -> Iterable[Tuple[Node, np.ndarray]]:
        split = np.array([
            border[1] + (border[2] - border[1]) * self.split,
            border[0] + (border[3] - border[0]) * self.split
        ])
        yield self.top, np.array([*border[:2], *split])
        yield self.bottom, np.array([*split[::-1], *border[2:]])


class XSplit(Node):

    def __init__(self, split: float, left: Node, right: Node):
        self.split = split
        self.left = left
        self.right = right

    def info(self):
        return f'{self.split}'

    def draw_on(self, image: Image, box: BoxT, debug=False):
        left_box, right_box = self.xsplit(box)
        self.left.draw_on(image, left_box, debug)
        self.right.draw_on(image, right_box, debug)
        if debug:
            self.draw_debug_info(image, box)

    def draw_debug_info(self, image: Image, box: BoxT):
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = box
        abs_split = int(x1 + self.split * (x2 - x1))
        draw.line(((abs_split, y1), (abs_split, y2)))

    def xsplit(self, box: BoxT) -> (BoxT, BoxT):
        x1, y1, x2, y2 = box
        abs_split = int(x1 + self.split * (x2 - x1))
        return (x1, y1, abs_split, y2), (abs_split, y1, x2, y2)

    def children(self):
        yield self.left
        yield self.right

    def children_border(self, border: np.ndarray) -> Iterable[Tuple[Node, np.ndarray]]:
        split = np.array([
            border[0] + (border[1] - border[0]) * self.split,
            border[3] + (border[2] - border[3]) * self.split
        ])
        yield self.left, np.array([border[0], *split, border[3]])
        yield self.right, np.array([split[0], border[1], border[2], split[1]])


class Pad(Node):

    def __init__(self, top: float, left: float, bottom: float, right: float, node: Node):
        self.ptop = top
        self.pleft = left
        self.pbottom = bottom
        self.pright = right
        self.node = node

    def info(self):
        return f'{self.ptop} {self.pleft} {self.pbottom} {self.pright}'

    def draw_on(self, image: Image, box: BoxT, debug=False):
        padded_box = self.pad(box)
        self.node.draw_on(image, padded_box, debug)
        if debug:
            self.draw_debug_info(image, box)

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

    def children(self):
        yield self.node

    def children_border(self, border: np.ndarray) -> Iterable[Tuple[Node, np.ndarray]]:
        # pad = np.array([
            # border[0] + (border[1] - border[0]) * self.split,
            # border[3] + (border[2] - border[3]) * self.split
        # ])
        # TODO
        yield self.node, border

class Rotate(Node):

    def __init__(self, angle_deg: float, node: Node):
        if isinstance(node, Rotate):
            self.angle_deg = (angle_deg + node.angle_deg) % 360
            self.node = node.node
        else:
            self.angle_deg = angle_deg % 360
            self.node = node

    def info(self):
        return f'{self.angle_deg}'

    def draw_on(self, image: Image, box: BoxT, debug=False):
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        img = Image.new('L', (w, h), 'white')
        self.node.draw_on(img, (0,0,w,h), debug=debug)
        if debug:
            draw = ImageDraw.Draw(img)
            draw.rectangle((1,1,w-1,h-1))
        rotated = img.rotate(self.angle_deg, fillcolor='white')
        image.paste(rotated, box=box)

    def children(self):
        yield self.node

    def children_border(self, border: np.ndarray) -> Iterable[Tuple[Node, np.ndarray]]:
        center = (border.min(axis=0) + border.max(axis=0)) / 2


        angle_rad = -self.angle_deg * math.pi / 180
        rotation = np.array([
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad),  math.cos(angle_rad)]
        ])
        import pdb
        pdb.set_trace()
        yield self.node, (rotation @ (border - center).T).T + center


class TextLeaf(Node):

    def __init__(self, text: str, font: ImageFont.FreeTypeFont):
        self.font = font
        self.text = text

    def info(self):
        return f'{self.font.path} {self.font.size} "{self.text[:10]}..."'

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
            self.draw_debug_info(image, box)

    def draw_debug_info(self, image: Image, box: BoxT):
        draw = ImageDraw.Draw(image)
        draw.rectangle(self.text_bbox, outline='red')


class FormulaLeaf(Node):
    pass

class ImageLeaf(Node):
    pass
