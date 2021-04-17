from djvu import decode

import argparse
import cairo
import numpy as np


cairo_pixel_format = cairo.FORMAT_ARGB32
djvu_pixel_format = decode.PixelFormatRgbMask(0xaFF0000, 0xFF00, 0xFF, bpp=32)
djvu_pixel_format.rows_top_to_bottom = 1
djvu_pixel_format.y_top_to_bottom = 0


class Context(decode.Context):

    def __init__(self, filename):
        self.filename = filename

    def convert_pages_to_surface(self, begin, end, mode):
        document = self.new_document(decode.FileURI(self.filename))
        document.decoding_job.wait()
        res = []
        counter = 0
        for page in document.pages:
            if counter < begin:
                counter += 1
                continue
            elif counter >= end:
                break
            counter += 1
            page_job = page.decode(wait=True)
            width, height = page_job.size
            rect = (0, 0, width, height)
            bytes_per_line = cairo.ImageSurface.format_stride_for_width(cairo_pixel_format, width)
            assert bytes_per_line % 4 == 0
            color_buffer = np.zeros((height, bytes_per_line // 4), dtype=np.uint32)
            try:
                page_job.render(mode, rect, rect, djvu_pixel_format, row_alignment=bytes_per_line, buffer=color_buffer)
            except decode.NotAvailable:
                res.append(cairo.ImageSurface.create_for_data(color_buffer, cairo_pixel_format, width, height))
                continue
            mask_buffer = np.zeros((height, bytes_per_line // 4), dtype=np.uint32)
            if mode == decode.RENDER_FOREGROUND:
                page_job.render(decode.RENDER_MASK_ONLY, rect, rect, djvu_pixel_format,
                                row_alignment=bytes_per_line, buffer=mask_buffer)
                mask_buffer <<= 24
                color_buffer |= mask_buffer
            color_buffer ^= 0xFF000000
            res.append(cairo.ImageSurface.create_for_data(color_buffer, cairo_pixel_format, width, height))
        return res


def convert_pages_to_numpy(filename, begin, end):
    parser = argparse.ArgumentParser()
    parser.set_defaults(mode=decode.RENDER_COLOR)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--foreground', dest='mode', action='store_const', const=decode.RENDER_FOREGROUND)
    group.add_argument('--background', dest='mode', action='store_const', const=decode.RENDER_BACKGROUND)
    group.add_argument('--mask', dest='mode', action='store_const', const=decode.RENDER_MASK_ONLY)
    parser.add_argument('djvu_path', metavar='DJVU-FILE')
    options = parser.parse_args([filename])
    res = []
    context = Context(filename)
    for surf in context.convert_pages_to_surface(begin, end, options.mode):
        res.append(np.ndarray(shape=(surf.get_height(), surf.get_width(), 4), dtype=np.uint8, buffer=surf.get_data()))
    return res
